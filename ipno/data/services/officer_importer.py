from tqdm import tqdm

from officers.models import Officer
from data.services.base_importer import BaseImporter
from data.constants import OFFICER_MODEL_NAME


ATTRIBUTES = [
    'uid',
    'last_name',
    'middle_name',
    'middle_initial',
    'first_name',
    'birth_year',
    'birth_month',
    'birth_day',
    'race',
    'gender',
]
BATCH_SIZE = 1000


class OfficerImporter(BaseImporter):
    data_model = OFFICER_MODEL_NAME

    def import_data(self, data):
        new_officers = []
        update_officers = []
        new_officer_uids = []

        officer_mappings = self.officer_mappings()
        for row in tqdm(data):
            officer_data = {attr: row[attr] if row[attr] else None for attr in ATTRIBUTES if attr in row}

            officer_id = officer_mappings.get(row['uid'])

            if officer_id:
                officer = Officer(**officer_data)
                officer.id = officer_id
                update_officers.append(officer)
            elif row['uid'] not in new_officer_uids:
                new_officer_uids.append(row['uid'])
                new_officers.append(
                    Officer(**officer_data)
                )

        update_officer_ids = [officer.id for officer in update_officers]
        delete_officers = Officer.objects.exclude(id__in=update_officer_ids)
        delete_officers_count = delete_officers.count()
        delete_officers.delete()

        Officer.objects.bulk_create(new_officers, batch_size=BATCH_SIZE)
        Officer.objects.bulk_update(update_officers, ATTRIBUTES, batch_size=BATCH_SIZE)

        return {
            'created_rows': len(new_officers),
            'updated_rows': len(update_officers),
            'deleted_rows': delete_officers_count,
        }
