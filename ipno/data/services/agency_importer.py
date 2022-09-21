import ast

from tqdm import tqdm

from data.services import BaseImporter
from data.constants import AGENCY_MODEL_NAME
from departments.models import Department


class AgencyImporter(BaseImporter):
    data_model = AGENCY_MODEL_NAME
    ATTRIBUTES = [
        'agency_slug',
        'agency_name',
        'location',
    ]

    UPDATE_ATTRIBUTES = ['name', 'location']

    def __init__(self):
        self.new_agency_attrs = []
        self.new_agency_slugs = []
        self.update_agency_attrs = []
        self.delete_agency_ids = []
        self.agency_mappings = {
            agency.slug: agency.id for agency in Department.objects.only('id', 'slug')
        }

    def handle_record_data(self, row):
        agency_data = self.parse_row_data(row, self.column_mappings)
        agency_slug = agency_data['agency_slug']
        agency_name = agency_data['agency_name']
        location = ast.literal_eval(agency_data['location']) if agency_data['location'] else None

        department_id = self.agency_mappings.get(agency_slug)

        department_data = {
            "name": agency_name,
            "slug": agency_slug,
            "location": location[::-1] if location else None,
        }

        if department_id:
            department_data['id'] = department_id
            self.update_agency_attrs.append(department_data)
        elif agency_slug not in self.new_agency_slugs:
            self.new_agency_slugs.append(agency_slug)
            self.new_agency_attrs.append(department_data)

    def import_data(self, data):
        for row in tqdm(data.get('added_rows'), desc='Create departments'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete departments'):
            agency_slug = row[self.column_mappings['agency_slug']]
            agency_id = self.agency_mappings.get(agency_slug)
            if agency_id:
                self.delete_agency_ids.append(agency_id)

        for row in tqdm(data.get('updated_rows'), desc='Update departments'):
            self.handle_record_data(row)

        return self.bulk_import(Department, self.new_agency_attrs, self.update_agency_attrs, self.delete_agency_ids)
