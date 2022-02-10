from itertools import chain

from django.template.defaultfilters import slugify
from tqdm import tqdm

from use_of_forces.models import UseOfForce
from data.services.base_importer import BaseImporter
from data.constants import USE_OF_FORCE_MODEL_NAME


class UofImporter(BaseImporter):
    data_model = USE_OF_FORCE_MODEL_NAME
    ATTRIBUTES = [
        'uof_uid',
        'uof_tracking_number',
        'force_description',
        'force_type',
        'force_level',
        'effective_uof',
        'accidental_discharge',
        'less_than_lethal',
        'status',
        'source',
        'service_type',
        'county',
        'traffic_stop',
        'sustained',
        'force_reason',
        'weather_description',
        'distance_from_officer',
        'body_worn_camera_available',
        'app_used',
        'citizen_uid',
        'citizen_arrested',
        'citizen_hospitalized',
        'citizen_injured',
        'citizen_body_type',
        'citizen_height',
        'citizen_involvement',
        'disposition',
        'citizen_sex',
        'citizen_race',
        'citizen_age_1',
        'officer_current_supervisor',
        'officer_title',
        'officer_injured',
        'officer_age',
        'officer_type',
        'officer_employment_status',
        'officer_department',
        'officer_division',
        'officer_sub_division_a',
        'officer_sub_division_b',

    ]

    INT_ATTRIBUTES = [
        'report_year',
        'citizen_age',
        'officer_years_exp',
        'officer_years_with_unit',
    ]

    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + ['officer_id', 'department_id']

    def __init__(self):
        self.new_uofs_attrs = []
        self.update_uofs_attrs = []
        self.new_uof_uids = []
        self.delete_uofs_ids = []
        self.officer_mappings = {}
        self.department_mappings = {}
        self.uof_mappings = {}

    def handle_record_data(self, row):
        agency = row[self.column_mappings['agency']]
        officer_uid = row[self.column_mappings['uid']]
        uof_data = self.parse_row_data(row, self.column_mappings)

        uof_uid = uof_data['uof_uid']

        formatted_agency = self.format_agency(agency)
        department_id = self.department_mappings.get(slugify(formatted_agency))
        uof_data['department_id'] = department_id

        officer_id = self.officer_mappings.get(officer_uid)
        uof_data['officer_id'] = officer_id

        uof_id = self.uof_mappings.get(uof_uid)

        if uof_id:
            uof_data['id'] = uof_id
            self.update_uofs_attrs.append(uof_data)
        elif uof_uid not in self.new_uof_uids:
            self.new_uof_uids.append(uof_uid)
            self.new_uofs_attrs.append(uof_data)

    def import_data(self, data):
        saved_data = list(chain(
            data.get('added_rows', []),
            data.get('updated_rows', []),
        ))
        deleted_data = data.get('deleted_rows', [])

        self.officer_mappings = self.get_officer_mappings()
        agencies = {row[self.column_mappings['agency']] for row in saved_data if row[self.column_mappings['agency']]}
        agencies.update([
            row[self.old_column_mappings['agency']] for row in deleted_data if row[self.old_column_mappings['agency']]
        ])
        self.department_mappings = self.get_department_mappings(agencies)

        self.uof_mappings = self.get_uof_mappings()

        for row in tqdm(data.get('added_rows'), desc='Create new uofs'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed uofs'):
            uof_uid = row[self.old_column_mappings['uof_uid']]
            uof_id = self.uof_mappings.get(uof_uid)
            if uof_id:
                self.delete_uofs_ids.append(uof_id)

        for row in tqdm(data.get('updated_rows'), desc='Update modified uofs'):
            self.handle_record_data(row)

        return self.bulk_import(UseOfForce, self.new_uofs_attrs, self.update_uofs_attrs, self.delete_uofs_ids)
