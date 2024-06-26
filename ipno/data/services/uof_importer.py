from tqdm import tqdm

from data.constants import USE_OF_FORCE_MODEL_NAME
from data.services.base_importer import BaseImporter
from data.services.data_reconciliation import DataReconciliation
from use_of_forces.models import UseOfForce


class UofImporter(BaseImporter):
    data_model = USE_OF_FORCE_MODEL_NAME

    ATTRIBUTES = list(
        {field.name for field in UseOfForce._meta.fields}
        - UseOfForce.BASE_FIELDS
        - UseOfForce.CUSTOM_FIELDS
    )
    UPDATE_ATTRIBUTES = ATTRIBUTES + ["department_id", "officer_id"]

    def __init__(self, csv_file_path):
        self.new_uofs_attrs = []
        self.update_uofs_attrs = []
        self.new_uof_uids = []
        self.delete_uofs_ids = []
        self.officer_mappings = {}
        self.department_mappings = {}
        self.uof_mappings = {}

        self.data_reconciliation = DataReconciliation(
            USE_OF_FORCE_MODEL_NAME, csv_file_path
        )

    def handle_record_data(self, row):
        agency = row[self.column_mappings["agency"]]
        officer_uid = row[self.column_mappings["uid"]]
        uof_data = self.parse_row_data(row, self.column_mappings)

        uof_uid = uof_data["uof_uid"]
        department_id = self.department_mappings[agency]
        uof_data["department_id"] = department_id
        officer_id = self.officer_mappings[officer_uid]
        uof_data["officer_id"] = officer_id

        uof_id = self.uof_mappings.get(uof_uid)

        if uof_id:
            uof_data["id"] = uof_id
            self.update_uofs_attrs.append(uof_data)
        elif uof_uid not in self.new_uof_uids:
            self.new_uof_uids.append(uof_uid)
            self.new_uofs_attrs.append(uof_data)

    def import_data(self, data):
        self.officer_mappings = self.get_officer_mappings()
        self.department_mappings = self.get_department_mappings()
        self.uof_mappings = self.get_uof_mappings()

        for row in tqdm(data.get("added_rows"), desc="Create new uofs"):
            self.handle_record_data(row)

        for row in tqdm(data.get("deleted_rows"), desc="Delete removed uofs"):
            uof_uid = row[self.old_column_mappings["uof_uid"]]
            uof_id = self.uof_mappings.get(uof_uid)
            if uof_id:
                self.delete_uofs_ids.append(uof_id)

        for row in tqdm(data.get("updated_rows"), desc="Update modified uofs"):
            self.handle_record_data(row)

        return self.bulk_import(
            UseOfForce,
            self.new_uofs_attrs,
            self.update_uofs_attrs,
            self.delete_uofs_ids,
        )
