from itertools import chain

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

    def __init__(self):
        self.new_people_attrs = []
        self.update_people_attrs = []
        self.new_person_ids = []
        self.delete_people_ids = []
        self.officer_mappings = {}
        self.person_mappings = {}

    def get_person_mappings(self):
        return {person.person_id: person.id for person in Person.objects.only('person_id', 'id')}

    def update_relations(self, raw_data):
        saved_data = list(chain(
            raw_data.get('added_rows', []),
            raw_data.get('updated_rows', []),
        ))
        deleted_data = raw_data.get('deleted_rows', [])
        update_officers_attrs = []

        officer_mappings = self.get_officer_mappings()
        person_mappings = self.get_person_mappings()

        for row in tqdm(saved_data, desc='Update saved officer - person relation'):
            for uid in row[self.column_mappings['uids']].split(','):
                officer_id = officer_mappings.get(uid.strip())

                if officer_id:
                    person_id = person_mappings.get(row[self.column_mappings['person_id']])
                    officer_data = {
                        'id': officer_id,
                        'person_id': person_id,
                    }
                    update_officers_attrs.append(officer_data)

        for row in tqdm(deleted_data, desc='Update deleted officer - person relation'):
            for old_uid in row[self.old_column_mappings['uids']].split(','):
                officer_id = officer_mappings.get(old_uid.strip())

                if officer_id:
                    person_id = person_mappings.get(row[self.column_mappings['person_id']])
                    officer_data = {
                        'id': officer_id,
                        'person_id': person_id,
                    }
                    update_officers_attrs.append(officer_data)

        for i in range(0, len(update_officers_attrs), self.BATCH_SIZE):
            update_objects = [Officer(**attrs) for attrs in update_officers_attrs[i:i + self.BATCH_SIZE]]
            Officer.objects.bulk_update(update_objects, ['person_id'])

        return len(update_officers_attrs)

    def handle_record_data(self, row):
        canonical_uid = row[self.column_mappings['canonical_uid']]
        person_data = self.parse_row_data(row, self.column_mappings)

        person_id = person_data['person_id']
        person_data['canonical_officer_id'] = self.officer_mappings.get(canonical_uid)

        person_key = self.person_mappings.get(person_id)

        if person_key:
            person_data['id'] = person_key
            self.update_people_attrs.append(person_data)
        elif person_id not in self.new_person_ids:
            self.new_person_ids.append(person_id)
            self.new_people_attrs.append(person_data)

    def import_data(self, data):
        self.officer_mappings = self.get_officer_mappings()
        self.person_mappings = self.get_person_mappings()

        for row in tqdm(data.get('added_rows'), desc='Create new people'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed people'):
            person_id = row[self.column_mappings['person_id']]
            person_key = self.person_mappings.get(person_id)
            if person_key:
                self.delete_people_ids.append(person_key)

        for row in tqdm(data.get('updated_rows'), desc='Update modified people'):
            self.handle_record_data(row)

        import_result = self.bulk_import(Person, self.new_people_attrs, self.update_people_attrs, self.delete_people_ids)

        self.update_relations(data)

        return import_result
