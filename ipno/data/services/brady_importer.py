from tqdm import tqdm

from brady.models import Brady
from data.constants import BRADY_MODEL_NAME
from data.services.base_importer import BaseImporter


class BradyImporter(BaseImporter):  # pragma: no cover
    data_model = BRADY_MODEL_NAME

    ATTRIBUTES = list(
        {field.name for field in Brady._meta.fields}
        - Brady.BASE_FIELDS
        - Brady.CUSTOM_FIELDS
    )

    UPDATE_ATTRIBUTES = ATTRIBUTES + ["officer_id", "department_id"]

    def __init__(self):
        self.new_brady_attrs = []
        self.update_brady_attrs = []
        self.new_brady_uids = []
        self.delete_brady_ids = []
        self.officer_mappings = {}
        self.department_mappings = {}
        self.brady_mappings = {}

    def handle_record_data(self, row):
        uid = row[self.column_mappings["uid"]]
        officer_id = self.officer_mappings[uid]

        agency = row[self.column_mappings["agency"]]
        department_id = self.department_mappings[agency]

        brady_data = self.parse_row_data(row, self.column_mappings)
        brady_uid = brady_data["brady_uid"]

        brady_id = self.brady_mappings.get(brady_uid)
        brady_data["officer_id"] = officer_id
        brady_data["department_id"] = department_id

        if brady_id:
            brady_data["id"] = brady_id
            self.update_brady_attrs.append(brady_data)
        elif brady_uid not in self.new_brady_uids:
            self.new_brady_uids.append(brady_uid)
            self.new_brady_attrs.append(brady_data)

    def import_data(self, data):
        self.brady_mappings = self.get_brady_mappings()
        self.officer_mappings = self.get_officer_mappings()
        self.department_mappings = self.get_department_mappings()

        for row in tqdm(data.get("added_rows"), desc="Create new brady"):
            self.handle_record_data(row)

        for row in tqdm(data.get("deleted_rows"), desc="Delete removed brady"):
            brady_uid = row[self.old_column_mappings["brady_uid"]]
            brady_id = self.brady_mappings.get(brady_uid)
            if brady_id:
                self.delete_brady_ids.append(brady_id)

        for row in tqdm(data.get("updated_rows"), desc="Update modified brady"):
            self.handle_record_data(row)

        return self.bulk_import(
            Brady,
            self.new_brady_attrs,
            self.update_brady_attrs,
            self.delete_brady_ids,
        )
