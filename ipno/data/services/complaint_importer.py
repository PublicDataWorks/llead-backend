from itertools import chain

from tqdm import tqdm

from complaints.models import Complaint
from data.constants import COMPLAINT_MODEL_NAME
from data.services.base_importer import BaseImporter
from data.services.data_reconciliation import DataReconciliation


class ComplaintImporter(BaseImporter):
    data_model = COMPLAINT_MODEL_NAME

    ATTRIBUTES = list(
        {field.name for field in Complaint._meta.fields}
        - Complaint.BASE_FIELDS
        - Complaint.CUSTOM_FIELDS
    )
    UPDATE_ATTRIBUTES = ATTRIBUTES

    def __init__(self, csv_file_path):
        self.new_complaints_attrs = []
        self.update_complaints_attrs = []
        self.new_allegation_uids = []
        self.delete_complaints_ids = []
        self.complaint_mappings = {}

        self.data_reconciliation = DataReconciliation(
            COMPLAINT_MODEL_NAME, csv_file_path
        )

    def update_relations(self, raw_data):
        saved_data = list(
            chain(
                raw_data.get("added_rows", []),
                raw_data.get("updated_rows", []),
            )
        )
        deleted_data = raw_data.get("deleted_rows", [])
        modified_complaints_ids = []

        DepartmentRelation = Complaint.departments.through
        OfficerRelation = Complaint.officers.through
        department_relation_ids = {}
        officer_relation_ids = {}

        officer_mappings = self.get_officer_mappings()
        agencies = {
            row[self.column_mappings["agency"]]
            for row in saved_data
            if row[self.column_mappings["agency"]]
        }
        agencies.update(
            [
                row[self.old_column_mappings["agency"]]
                for row in deleted_data
                if row[self.old_column_mappings["agency"]]
            ]
        )
        department_mappings = self.get_department_mappings()

        complaint_mappings = self.get_complaint_mappings()

        for row in tqdm(saved_data, desc="Update complaints' relations"):
            officer_uid = row[self.column_mappings["uid"]]
            agency = row[self.column_mappings["agency"]]
            complaint_data = self.parse_row_data(row, self.column_mappings)

            if officer_uid or agency:
                allegation_uid = complaint_data.get("allegation_uid")

                complaint_id = complaint_mappings.get(allegation_uid)

                if complaint_id:
                    modified_complaints_ids.append(complaint_id)

                    if officer_uid:
                        officer_id = officer_mappings.get(officer_uid)
                        if officer_id:
                            officer_relation_ids[complaint_id] = officer_id

                    if agency:
                        department_id = department_mappings[agency]

                        department_relation_ids[complaint_id] = department_id
        department_relations = [
            DepartmentRelation(complaint_id=complaint_id, department_id=department_id)
            for complaint_id, department_id in department_relation_ids.items()
        ]

        officer_relations = [
            OfficerRelation(complaint_id=complaint_id, officer_id=officer_id)
            for complaint_id, officer_id in officer_relation_ids.items()
        ]

        DepartmentRelation.objects.filter(
            complaint_id__in=modified_complaints_ids
        ).delete()
        DepartmentRelation.objects.bulk_create(
            department_relations, batch_size=self.BATCH_SIZE
        )

        OfficerRelation.objects.filter(
            complaint_id__in=modified_complaints_ids
        ).delete()
        OfficerRelation.objects.bulk_create(
            officer_relations, batch_size=self.BATCH_SIZE
        )

    def handle_record_data(self, row):
        complaint_data = self.parse_row_data(row, self.column_mappings)
        allegation_uid = complaint_data["allegation_uid"]

        complaint_id = self.complaint_mappings.get(allegation_uid)

        if complaint_id:
            complaint_data["id"] = complaint_id
            self.update_complaints_attrs.append(complaint_data)
        elif allegation_uid not in self.new_allegation_uids:
            self.new_complaints_attrs.append(complaint_data)
            self.new_allegation_uids.append(allegation_uid)

    def import_data(self, data):
        self.complaint_mappings = self.get_complaint_mappings()

        for row in tqdm(data.get("added_rows"), desc="Create new complaints"):
            self.handle_record_data(row)

        for row in tqdm(data.get("deleted_rows"), desc="Delete removed complaints"):
            complaint_data = self.parse_row_data(row, self.old_column_mappings)
            allegation_uid = complaint_data.get("allegation_uid")

            complaint_id = self.complaint_mappings.get(allegation_uid)
            self.delete_complaints_ids.append(complaint_id)

        for row in tqdm(data.get("updated_rows"), desc="Update modified complaints"):
            self.handle_record_data(row)

        import_result = self.bulk_import(
            Complaint,
            self.new_complaints_attrs,
            self.update_complaints_attrs,
            self.delete_complaints_ids,
        )
        self.update_relations(data)

        return import_result
