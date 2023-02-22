import traceback
from datetime import datetime

from django.utils.text import slugify

import pytz
from tqdm import tqdm
from wrgl import Repository

from appeals.models import Appeal
from complaints.models import Complaint
from data.constants import (
    IMPORT_LOG_STATUS_ERROR,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_NO_NEW_COMMIT,
    IMPORT_LOG_STATUS_NO_NEW_DATA,
    IMPORT_LOG_STATUS_RUNNING,
    IMPORT_LOG_STATUS_STARTED,
)
from data.models import ImportLog, WrglRepo
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
    BATCH_SIZE = 500
    WRGL_OFFSET_BATCH_SIZE = 1000
    branch = "main"
    new_commit = None
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

    def process_wrgl_data(self, old_commit_hash):
        diff_result = self.repo.diff(self.new_commit.sum, old_commit_hash)
        if not diff_result.row_diff:
            return

        old_commit = self.repo.get_commit(old_commit_hash)

        old_columns = old_commit.table.columns
        self.old_column_mappings = {
            column: old_columns.index(column) for column in old_columns
        }

        added_rows = []
        deleted_rows = []
        modified_rows_old = []

        added_rows_offsets = [r.off1 for r in diff_result.row_diff if r.off2 is None]
        removed_rows_offsets = [r.off2 for r in diff_result.row_diff if r.off1 is None]
        modified_rows_offsets = [
            r.off1
            for r in diff_result.row_diff
            if r.off1 is not None and r.off2 is not None
        ]

        with tqdm(
            total=len(added_rows_offsets), desc="Downloading created data"
        ) as pbar:
            for i in range(0, len(added_rows_offsets), self.WRGL_OFFSET_BATCH_SIZE):
                added_rows.extend(
                    list(
                        self.repo.get_table_rows(
                            self.new_commit.table.sum,
                            added_rows_offsets[i : i + self.WRGL_OFFSET_BATCH_SIZE],
                        )
                    )
                )
                pbar.update(self.WRGL_OFFSET_BATCH_SIZE)

        with tqdm(
            total=len(removed_rows_offsets), desc="Downloading deleted data"
        ) as pbar:
            for i in range(0, len(removed_rows_offsets), self.WRGL_OFFSET_BATCH_SIZE):
                deleted_rows.extend(
                    list(
                        self.repo.get_table_rows(
                            old_commit.table.sum,
                            removed_rows_offsets[i : i + self.WRGL_OFFSET_BATCH_SIZE],
                        )
                    )
                )
                pbar.update(self.WRGL_OFFSET_BATCH_SIZE)

        with tqdm(
            total=len(modified_rows_offsets), desc="Downloading modified data"
        ) as pbar:
            for i in range(0, len(modified_rows_offsets), self.WRGL_OFFSET_BATCH_SIZE):
                modified_rows_old.extend(
                    list(
                        self.repo.get_table_rows(
                            self.new_commit.table.sum,
                            modified_rows_offsets[i : i + self.WRGL_OFFSET_BATCH_SIZE],
                        )
                    )
                )
                pbar.update(self.WRGL_OFFSET_BATCH_SIZE)

        return {
            "added_rows": added_rows,
            "deleted_rows": deleted_rows,
            "updated_rows": modified_rows_old,
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

    def retrieve_wrgl_data(self, branch):
        self.repo = Repository("https://wrgl.llead.co/")

        self.new_commit = self.repo.get_branch(branch)

        columns = self.new_commit.table.columns
        self.column_mappings = {column: columns.index(column) for column in columns}

    def process(self):
        import_log = ImportLog.objects.create(
            data_model=self.data_model,
            status=IMPORT_LOG_STATUS_STARTED,
            started_at=datetime.now(pytz.utc),
        )
        wrgl_repo = WrglRepo.objects.filter(data_model=self.data_model).first()

        if wrgl_repo:
            self.update_import_log(
                import_log,
                {
                    "repo_name": wrgl_repo.repo_name,
                },
            )

            self.retrieve_wrgl_data(wrgl_repo.repo_name)

            commit_hash = wrgl_repo.latest_commit_hash

            if commit_hash:
                current_hash = wrgl_repo.commit_hash
                if current_hash != commit_hash:
                    self.update_import_log(
                        import_log,
                        {
                            "commit_hash": commit_hash,
                            "status": IMPORT_LOG_STATUS_RUNNING,
                        },
                    )
                    try:
                        if current_hash:
                            data = self.process_wrgl_data(current_hash)
                        else:
                            all_rows = list(
                                self.repo.get_blocks(
                                    f"heads/{wrgl_repo.repo_name}",
                                    with_column_names=False,
                                )
                            )
                            data = {
                                "added_rows": all_rows,
                                "deleted_rows": [],
                                "updated_rows": [],
                            }

                        if data:
                            import_results = self.import_data(data)
                            wrgl_repo.commit_hash = commit_hash
                            wrgl_repo.save()
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
                            wrgl_repo.commit_hash = commit_hash
                            wrgl_repo.save()
                            self.update_import_log(
                                import_log,
                                {
                                    "commit_hash": commit_hash,
                                    "status": IMPORT_LOG_STATUS_NO_NEW_DATA,
                                    "finished_at": datetime.now(pytz.utc),
                                },
                            )
                    except Exception as e:
                        self.update_import_log(
                            import_log,
                            {
                                "status": IMPORT_LOG_STATUS_ERROR,
                                "finished_at": datetime.now(pytz.utc),
                                "error_message": (
                                    "Error occurs while importing"
                                    f" data!\n{traceback.format_exc()}"
                                ),
                            },
                        )
                        raise e
                else:
                    self.update_import_log(
                        import_log,
                        {
                            "commit_hash": commit_hash,
                            "status": IMPORT_LOG_STATUS_NO_NEW_COMMIT,
                            "finished_at": datetime.now(pytz.utc),
                        },
                    )
            else:
                self.update_import_log(
                    import_log,
                    {
                        "status": IMPORT_LOG_STATUS_ERROR,
                        "finished_at": datetime.now(pytz.utc),
                        "error_message": (
                            "Cannot get latest commit hash from Wrgl for repo"
                            f" {wrgl_repo.repo_name}!"
                        ),
                    },
                )

        else:
            self.update_import_log(
                import_log,
                {
                    "status": IMPORT_LOG_STATUS_ERROR,
                    "finished_at": datetime.now(pytz.utc),
                    "error_message": "Cannot find Wrgl Repo!",
                },
            )
