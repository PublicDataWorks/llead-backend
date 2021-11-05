from tqdm import tqdm

from data.constants import PERSON_MODEL_NAME
from data.services import BaseImporter
from officers.models import Officer
from people.models import Person


class PersonImporter(BaseImporter):
    data_model = PERSON_MODEL_NAME

    ATTRIBUTES = [
        'canonical_officer_uid',
        'person_id',
    ]

    UPDATE_ATTRIBUTES = [
        'canonical_officer_id',
        'person_id',
        'all_complaints_count',
    ]

    def person_mappings(self):
        return {person.person_id: person.id for person in Person.objects.only('person_id', 'id')}

    def update_relations(self, data):
        update_officers_attrs = []

        officer_mappings = self.officer_mappings()
        person_mappings = self.person_mappings()

        for row in tqdm(data, desc='Update officer - person relation'):
            for uid in row['uids'].split(','):
                officer_id = officer_mappings.get(uid.strip())

                if officer_id:
                    person_id = person_mappings.get(row['person_id'])
                    officer_data = {
                        'id': officer_id,
                        'person_id': person_id,
                    }
                    update_officers_attrs.append(officer_data)

        for i in range(0, len(update_officers_attrs), self.BATCH_SIZE):
            update_objects = [Officer(**attrs) for attrs in update_officers_attrs[i:i + self.BATCH_SIZE]]
            Officer.objects.bulk_update(update_objects, ['person_id'])

        return len(update_officers_attrs)

    def import_data(self, data):
        new_people_attrs = []
        update_people_attrs = []
        new_person_ids = []

        officer_mappings = self.officer_mappings()
        person_mappings = self.person_mappings()

        for row in tqdm(data):
            person_id = row['person_id']
            canonical_uid = row['canonical_uid']

            person_data = self.parse_row_data(row)

            person_key = person_mappings.get(person_id)

            person_data['canonical_officer_id'] = officer_mappings.get(canonical_uid)

            if person_key:
                person_data['id'] = person_key
                update_people_attrs.append(person_data)
            elif person_id not in new_person_ids:
                new_person_ids.append(person_id)
                new_people_attrs.append(person_data)

        import_result = self.bulk_import(Person, new_people_attrs, update_people_attrs)

        updated_rows = self.update_relations(data)

        import_result['updated_rows'] += updated_rows
        return import_result
