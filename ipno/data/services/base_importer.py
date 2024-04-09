import traceback
from datetime import datetime

from django.utils.text import slugify

import pytz

from appeals.models import Appeal
from brady.models import Brady
from complaints.models import Complaint
from data.constants import (
    IMPORT_LOG_STATUS_ERROR,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_NO_NEW_DATA,
    IMPORT_LOG_STATUS_STARTED,
)
from data.models import ImportLog
from departments.models import Department
from officers.models import Officer
from use_of_forces.models import UseOfForce
from utils.parse_utils import parse_int


class BaseImporter(object):
    data_model = None
    ATTRIBUTES = []
    NA_ATTRIBUTES = []
    INT_ATTRIBUTES = []
    SLUG_ATTRIBUTES = []
    DATE_ATTRIBUTES = []
    BATCH_SIZE = 500
    column_mappings = {}
    old_column_mappings = {}

    def parse_row_data(self, row, mappings):
        row_data = {
            attr: row[mappings[attr]] if row[mappings[attr]] else None
            for attr in self.ATTRIBUTES
            if attr in mappings
        }

        for attr in self.NA_ATTRIBUTES:
            row_data[attr] = (
                row[mappings[attr]] if row[mappings[attr]] != "NA" else None
            )

        for attr in self.INT_ATTRIBUTES:
            row_data[attr] = (
                parse_int(row[mappings[attr]]) if row[mappings[attr]] else None
            )

        for attr in self.SLUG_ATTRIBUTES:
            row_data[attr] = (
                slugify(row[mappings[attr]]) if row[mappings[attr]] else None
            )

        for attr in self.DATE_ATTRIBUTES:
            row_data[attr] = (
                datetime.strptime(row[mappings[attr]], "%m/%d/%Y").date()
                if row[mappings[attr]]
                else None
            )

        return row_data

    def get_department_mappings(self):
        slugify_mappings = {
            department.agency_slug: department.id
            for department in Department.objects.only("id", "agency_slug")
        }

        return slugify_mappings

    def get_officer_mappings(self):
        return {
            officer.uid: officer.id for officer in Officer.objects.only("id", "uid")
        }

    def get_uof_mappings(self):
        return {
            use_of_force.uof_uid: use_of_force.id
            for use_of_force in UseOfForce.objects.only("id", "uof_uid")
        }

    def get_appeal_mappings(self):
        return {
            appeal.appeal_uid: appeal.id
            for appeal in Appeal.objects.only("id", "appeal_uid")
        }

    def get_complaint_mappings(self):
        return {
            complaint.allegation_uid: complaint.id
            for complaint in Complaint.objects.only("id", "allegation_uid")
        }

    def get_brady_mappings(self):
        return {
            brady.brady_uid: brady.id for brady in Brady.objects.only("id", "brady_uid")
        }

    def bulk_import(
        self,
        klass,
        new_items_attrs,
        update_items_attrs,
        delete_items_ids,
        cleanup_action=None,
    ):
        delete_items = klass.objects.filter(id__in=delete_items_ids)

        if cleanup_action:
            cleanup_action(list(delete_items.values()))

        delete_items_count = delete_items.count()
        delete_items.delete()

        for i in range(0, len(new_items_attrs), self.BATCH_SIZE):
            new_objects = [
                klass(**attrs) for attrs in new_items_attrs[i : i + self.BATCH_SIZE]
            ]
            klass.objects.bulk_create(new_objects)

        for i in range(0, len(update_items_attrs), self.BATCH_SIZE):
            update_objects = [
                klass(**attrs) for attrs in update_items_attrs[i : i + self.BATCH_SIZE]
            ]
            klass.objects.bulk_update(update_objects, self.UPDATE_ATTRIBUTES)

        return {
            "created_rows": len(new_items_attrs),
            "updated_rows": len(update_items_attrs),
            "deleted_rows": delete_items_count,
        }

    def import_data(self, data):
        raise NotImplementedError

    def update_import_log(self, import_log, log_data):
        for key, value in log_data.items():
            setattr(import_log, key, value)
        import_log.save()

    def process(self):
        import_log = ImportLog.objects.create(
            data_model=self.data_model,
            status=IMPORT_LOG_STATUS_STARTED,
            started_at=datetime.now(pytz.utc),
        )

        try:
            data = self.data_reconciliation.reconcile_data()

            if (
                data.get("added_rows")
                or data.get("updated_rows")
                or data.get("deleted_rows")
            ):
                self.column_mappings = data["columns_mapping"]
                self.old_column_mappings = data[
                    "columns_mapping"
                ]  # Add this for backward compatibility only, TODO: remove

                import_results = self.import_data(data)

                self.update_import_log(
                    import_log,
                    {
                        "status": IMPORT_LOG_STATUS_FINISHED,
                        "finished_at": datetime.now(pytz.utc),
                        "created_rows": import_results.get("created_rows"),
                        "updated_rows": import_results.get("updated_rows"),
                        "deleted_rows": import_results.get("deleted_rows"),
                    },
                )

                return True
            else:
                self.update_import_log(
                    import_log,
                    {
                        "status": IMPORT_LOG_STATUS_NO_NEW_DATA,
                        "finished_at": datetime.now(pytz.utc),
                    },
                )

                return False
        except Exception as e:
            self.update_import_log(
                import_log,
                {
                    "status": IMPORT_LOG_STATUS_ERROR,
                    "finished_at": datetime.now(pytz.utc),
                    "error_message": (
                        f"Error occurs while importing data!\n{traceback.format_exc()}"
                    ),
                },
            )
            raise e
