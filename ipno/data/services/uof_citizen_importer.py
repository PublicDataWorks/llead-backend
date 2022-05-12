from tqdm import tqdm

from data.services.base_importer import BaseImporter
from data.constants import USE_OF_FORCE_CITIZEN_MODEL_NAME
from use_of_forces.models import UseOfForceCitizen


class UofCitizenImporter(BaseImporter):
    data_model = USE_OF_FORCE_CITIZEN_MODEL_NAME
    ATTRIBUTES = [
        'uof_citizen_uid',
        'uof_uid',
        'citizen_influencing_factors',
        'citizen_distance_from_officer',
        'citizen_arrested',
        'citizen_arrest_charges',
        'citizen_hospitalized',
        'citizen_injured',
        'citizen_build',
        'citizen_height',
        'citizen_sex',
    ]

    UPDATE_ATTRIBUTES = ATTRIBUTES + ['use_of_force_id']

    def __init__(self):
        self.new_uof_citizens_attrs = []
        self.update_uof_citizens_attrs = []
        self.new_uof_citizen_uids = []
        self.delete_uof_citizen_ids = []
        self.officer_mappings = {}
        self.department_mappings = {}
        self.uof_citizen_mappings = {}

    def handle_record_data(self, row):
        uof_uid = row[self.column_mappings['uof_uid']]
        uof_id = self.uof_mappings.get(uof_uid)

        uof_citizen_data = self.parse_row_data(row, self.column_mappings)
        uof_citizen_uid = uof_citizen_data['uof_citizen_uid']

        uof_citizen_data['use_of_force_id'] = uof_id
        uof_citizen_id = self.uof_citizen_mappings.get((uof_citizen_uid, uof_uid))

        if uof_citizen_id:
            uof_citizen_data['id'] = uof_citizen_id
            self.update_uof_citizens_attrs.append(uof_citizen_data)
        elif (uof_citizen_uid, uof_uid) not in self.new_uof_citizen_uids:
            self.new_uof_citizen_uids.append((uof_citizen_uid, uof_uid))
            self.new_uof_citizens_attrs.append(uof_citizen_data)

    def import_data(self, data):
        self.officer_mappings = self.get_officer_mappings()
        self.uof_mappings = self.get_uof_mappings()
        self.uof_citizen_mappings = self.get_uof_citizen_mappings()

        for row in tqdm(data.get('added_rows'), desc='Create new uof_citizens'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed uof_citizens'):
            uof_citizen_uid = row[self.old_column_mappings['uof_citizen_uid']]
            uof_uid = row[self.old_column_mappings['uof_uid']]
            uof_citizen_id = self.uof_citizen_mappings.get((uof_citizen_uid, uof_uid))
            if uof_citizen_id:
                self.delete_uof_citizen_ids.append(uof_citizen_id)

        for row in tqdm(data.get('updated_rows'), desc='Update modified uof_citizens'):
            self.handle_record_data(row)

        return self.bulk_import(UseOfForceCitizen, self.new_uof_citizens_attrs, self.update_uof_citizens_attrs, self.delete_uof_citizen_ids)

    def get_uof_citizen_mappings(self):
        return {
            (use_of_force_citizen.uof_citizen_uid, use_of_force_citizen.uof_uid): use_of_force_citizen.id
            for use_of_force_citizen in UseOfForceCitizen.objects.only('id', 'uof_citizen_uid', 'uof_uid')
        }
