from tqdm import tqdm

from officers.models import Officer
from data.services.base_importer import BaseImporter
from data.constants import OFFICER_MODEL_NAME


class OfficerImporter(BaseImporter):
    data_model = OFFICER_MODEL_NAME
    ATTRIBUTES = [
        'uid',
        'last_name',
        'middle_name',
        'middle_initial',
        'first_name',
        'race',
        'gender',
    ]
    INT_ATTRIBUTES = [
        'birth_year',
        'birth_month',
        'birth_day',
    ]
    UPDATE_ONLY_ATTRIBUTES = [
        'is_name_changed',
    ]
    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + UPDATE_ONLY_ATTRIBUTES

    def __init__(self):
        self.new_officers_atrs = []
        self.update_officers_attrs = []
        self.new_officer_uids = []
        self.delete_officers_ids = []
        self.officer_mappings = {}
        self.officer_name_mappings = {}
        self.existed_officers_uids = []

    def get_officer_name_mappings(self):
        return {
            officer.uid: (officer.first_name, officer.last_name)
            for officer in Officer.objects.only('uid', 'first_name', 'last_name')
        }

    def handle_record_data(self, row):
        officer_data = self.parse_row_data(row, self.column_mappings)
        row_uid = officer_data['uid']

        if row_uid in self.existed_officers_uids:
            officer_id = self.officer_mappings.get(row_uid)

            officer_data['id'] = officer_id

            officer_names = self.officer_name_mappings.get(row_uid)

            officer_first_name = officer_names[0]
            officer_last_name = officer_names[1]

            if row[self.column_mappings['first_name']] != officer_first_name or row[self.column_mappings['last_name']] != officer_last_name:
                officer_data['is_name_changed'] = True

            self.update_officers_attrs.append(officer_data)
        elif row_uid not in self.new_officer_uids:
            self.new_officer_uids.append(row_uid)
            self.new_officers_atrs.append(officer_data)

    def import_data(self, data):
        self.officer_mappings = self.get_officer_mappings()
        self.officer_name_mappings = self.get_officer_name_mappings()
        self.existed_officers_uids = list(Officer.objects.all().values_list('uid', flat=True))

        for row in tqdm(data.get('added_rows'), desc='Create new officers'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed officers'):
            row_uid = row[self.old_column_mappings['uid']]
            officer_id = self.officer_mappings.get(row_uid)
            if officer_id:
                self.delete_officers_ids.append(officer_id)

        for row in tqdm(data.get('updated_rows'), desc='Update modified officers'):
            self.handle_record_data(row)

        return self.bulk_import(Officer, self.new_officers_atrs, self.update_officers_attrs, self.delete_officers_ids)
