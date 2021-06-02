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
    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES

    def import_data(self, data):
        new_officers_atrs = []
        update_officers_attrs = []
        new_officer_uids = []

        officer_mappings = self.officer_mappings()
        for row in tqdm(data):
            officer_data = self.parse_row_data(row)
            officer_id = officer_mappings.get(row['uid'])

            if officer_id:
                officer_data['id'] = officer_id
                update_officers_attrs.append(officer_data)
            elif row['uid'] not in new_officer_uids:
                new_officer_uids.append(row['uid'])
                new_officers_atrs.append(officer_data)

        return self.bulk_import(Officer, new_officers_atrs, update_officers_attrs)
