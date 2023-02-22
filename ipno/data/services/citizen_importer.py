from tqdm import tqdm

from citizens.models import Citizen
from data.constants import CITIZEN_MODEL_NAME
from data.services.base_importer import BaseImporter


class CitizenImporter(BaseImporter):
    data_model = CITIZEN_MODEL_NAME

    ATTRIBUTES = list(
        {field.name for field in Citizen._meta.fields}
        - Citizen.BASE_FIELDS
        - Citizen.CUSTOM_FIELDS
    )
    UPDATE_ATTRIBUTES = ATTRIBUTES + [
        "use_of_force_id",
        "complaint_id",
        "department_id",
    ]

    def __init__(self):
        self.new_citizens_attrs = []
        self.update_citizens_attrs = []
        self.new_citizen_uids = []
        self.delete_citizen_ids = []
        self.uof_mappings = {}
        self.complaint_mappings = {}
        self.department_mappings = {}
        self.citizen_mappings = {}

    def handle_record_data(self, row):
        agency = row[self.column_mappings["agency"]]
        department_id = self.department_mappings[agency]

        uof_uid = row[self.column_mappings["uof_uid"]]
        uof_id = self.uof_mappings.get(uof_uid)

        allegation_uid = row[self.column_mappings["allegation_uid"]]
        complaint_id = self.complaint_mappings.get(allegation_uid)

        citizen_data = self.parse_row_data(row, self.column_mappings)
        citizen_uid = citizen_data["citizen_uid"]

        citizen_id = self.citizen_mappings.get(citizen_uid)
        citizen_data["use_of_force_id"] = uof_id
        citizen_data["complaint_id"] = complaint_id
        citizen_data["department_id"] = department_id

        if citizen_id:
            citizen_data["id"] = citizen_id
            self.update_citizens_attrs.append(citizen_data)
        elif citizen_uid not in self.new_citizen_uids:
            self.new_citizen_uids.append(citizen_uid)
            self.new_citizens_attrs.append(citizen_data)

    def import_data(self, data):
        self.citizen_mappings = self.get_citizen_mappings()
        self.complaint_mappings = self.get_complaint_mappings()
        self.uof_mappings = self.get_uof_mappings()
        self.department_mappings = self.get_department_mappings()

        for row in tqdm(data.get("added_rows"), desc="Create new citizens"):
            self.handle_record_data(row)

        for row in tqdm(data.get("deleted_rows"), desc="Delete removed citizens"):
            citizen_uid = row[self.old_column_mappings["citizen_uid"]]
            citizen_id = self.citizen_mappings.get(citizen_uid)
            if citizen_id:
                self.delete_citizen_ids.append(citizen_id)

        for row in tqdm(data.get("updated_rows"), desc="Update modified citizens"):
            self.handle_record_data(row)

        return self.bulk_import(
            Citizen,
            self.new_citizens_attrs,
            self.update_citizens_attrs,
            self.delete_citizen_ids,
        )

    def get_citizen_mappings(self):
        return {
            citizen.citizen_uid: citizen.id
            for citizen in Citizen.objects.only("id", "citizen_uid")
        }
