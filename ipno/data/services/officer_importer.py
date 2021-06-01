from tqdm import tqdm

from officers.models import Officer
from data.services.base_importer import BaseImporter
from data.constants import OFFICER_MODEL_NAME

BATCH_SIZE = 1000


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

        update_officer_ids = [attrs['id'] for attrs in update_officers_attrs]
        delete_officers = Officer.objects.exclude(id__in=update_officer_ids)
        delete_officers_count = delete_officers.count()
        delete_officers.delete()

        for i in range(0, len(new_officers_atrs), BATCH_SIZE):
            new_objects = [Officer(**attrs) for attrs in new_officers_atrs[i:i + BATCH_SIZE]]
            Officer.objects.bulk_create(new_objects)

        for i in range(0, len(update_officers_attrs), BATCH_SIZE):
            update_objects = [Officer(**attrs) for attrs in update_officers_attrs[i:i + BATCH_SIZE]]
            Officer.objects.bulk_update(update_objects, self.UPDATE_ATTRIBUTES)

        return {
            'created_rows': len(new_officers_atrs),
            'updated_rows': len(update_officers_attrs),
            'deleted_rows': delete_officers_count,
        }
