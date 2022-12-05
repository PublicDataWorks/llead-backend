from tqdm import tqdm

from data.constants import USE_OF_FORCE_OFFICER_MODEL_NAME
from data.services.base_importer import BaseImporter
from use_of_forces.models import UseOfForceOfficer


class UofOfficerImporter(BaseImporter):
    data_model = USE_OF_FORCE_OFFICER_MODEL_NAME
    ATTRIBUTES = [
        "uof_uid",
        "uid",
        "use_of_force_description",
        "use_of_force_level",
        "use_of_force_effective",
        "officer_injured",
    ]

    INT_ATTRIBUTES = [
        "age",
        "years_of_service",
    ]

    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + ["officer_id", "use_of_force_id"]

    def __init__(self):
        self.new_uof_officers_attrs = []
        self.update_uof_officers_attrs = []
        self.new_uof_officer_ids = []
        self.delete_uof_officer_ids = []
        self.officer_mappings = {}
        self.uof_mappings = {}
        self.uof_officer_mappings = {}

    def handle_record_data(self, row):
        officer_uid = row[self.column_mappings["uid"]]
        uof_data = self.parse_row_data(row, self.column_mappings)

        uof_uid = uof_data["uof_uid"]

        officer_id = self.officer_mappings.get(officer_uid)
        uof_data["officer_id"] = officer_id

        use_of_force_id = self.uof_mappings.get(uof_uid)
        uof_data["use_of_force_id"] = use_of_force_id

        uof_officer_id = (uof_uid, officer_uid)
        uof_id = self.uof_officer_mappings.get(uof_officer_id)

        if uof_id:
            uof_data["id"] = uof_id
            self.update_uof_officers_attrs.append(uof_data)
        elif uof_officer_id not in self.new_uof_officer_ids:
            self.new_uof_officer_ids.append(uof_officer_id)
            self.new_uof_officers_attrs.append(uof_data)

    def import_data(self, data):
        self.officer_mappings = self.get_officer_mappings()
        self.uof_mappings = self.get_uof_mappings()
        self.uof_officer_mappings = self.get_uof_officer_mappings()

        for row in tqdm(data.get("added_rows"), desc="Create new uof_officers"):
            self.handle_record_data(row)

        for row in tqdm(data.get("deleted_rows"), desc="Delete removed uof_officers"):
            uof_uid = row[self.old_column_mappings["uof_uid"]]
            uid = row[self.old_column_mappings["uid"]]
            uof_officer_id = self.uof_officer_mappings.get((uof_uid, uid))

            if uof_officer_id:
                self.delete_uof_officer_ids.append(uof_officer_id)

        for row in tqdm(data.get("updated_rows"), desc="Update modified uof_officers"):
            self.handle_record_data(row)

        return self.bulk_import(
            UseOfForceOfficer,
            self.new_uof_officers_attrs,
            self.update_uof_officers_attrs,
            self.delete_uof_officer_ids,
        )

    def get_uof_officer_mappings(self):
        return {
            (
                use_of_force_officer.uof_uid,
                use_of_force_officer.uid,
            ): use_of_force_officer.id
            for use_of_force_officer in UseOfForceOfficer.objects.only(
                "id", "uof_uid", "uid"
            )
        }
