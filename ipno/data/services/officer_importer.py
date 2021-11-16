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

    def officer_name_mappings(self):
        return {
            officer.uid: (officer.first_name, officer.last_name)
            for officer in Officer.objects.only('uid', 'first_name', 'last_name')
        }

    def import_data(self, data):
        new_officers_atrs = []
        update_officers_attrs = []
        new_officer_uids = []

        officer_mappings = self.officer_mappings()
        officer_name_mappings = self.officer_name_mappings()

        for row in tqdm(data):
            row_uid = row['uid']
            officer_data = self.parse_row_data(row)
            officer_id = officer_mappings.get(row_uid)

            if officer_id:
                officer_data['id'] = officer_id

                officer_names = officer_name_mappings.get(row_uid)

                officer_first_name = officer_names[0]
                officer_last_name = officer_names[1]

                if row['first_name'] != officer_first_name or row['last_name'] != officer_last_name:
                    officer_data['is_name_changed'] = True

                update_officers_attrs.append(officer_data)

            elif row_uid not in new_officer_uids:
                new_officer_uids.append(row_uid)
                new_officers_atrs.append(officer_data)

        return self.bulk_import(Officer, new_officers_atrs, update_officers_attrs)
