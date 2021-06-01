from tqdm import tqdm

from use_of_forces.models import UseOfForce
from data.services.base_importer import BaseImporter
from data.constants import USE_OF_FORCE_MODEL_NAME

BATCH_SIZE = 1000


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
        'data_production_year',
    ]

    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + ['officer_id', 'department_id']

    def import_data(self, data):
        new_uofs_attrs = []
        update_uofs_attrs = []
        new_uof_uids = []

        officer_mappings = self.officer_mappings()
        agencies = {row['agency'] for row in data if row['agency']}
        department_mappings = self.department_mappings(agencies)

        uof_mappings = self.uof_mappings()

        for row in tqdm(data):
            agency = row['agency']
            uof_uid = row['uof_uid']
            officer_uid = row['uid']

            uof_data = self.parse_row_data(row)
            formatted_agency = self.format_agency(agency)
            department_id = department_mappings.get(formatted_agency)
            uof_data['department_id'] = department_id

            officer_id = officer_mappings.get(officer_uid)
            uof_data['officer_id'] = officer_id

            uof_id = uof_mappings.get(uof_uid)

            if uof_id:
                uof_data['id'] = uof_id
                update_uofs_attrs.append(uof_data)
            elif uof_uid not in new_uof_uids:
                new_uof_uids.append(uof_uid)
                new_uofs_attrs.append(uof_data)

        update_uof_ids = [attrs['id'] for attrs in update_uofs_attrs]
        delete_uofs = UseOfForce.objects.exclude(id__in=update_uof_ids)
        delete_uofs_count = delete_uofs.count()
        delete_uofs.delete()

        for i in range(0, len(new_uofs_attrs), BATCH_SIZE):
            new_objects = [UseOfForce(**attrs) for attrs in new_uofs_attrs[i:i + BATCH_SIZE]]
            UseOfForce.objects.bulk_create(new_objects)

        for i in range(0, len(update_uofs_attrs), BATCH_SIZE):
            update_objects = [UseOfForce(**attrs) for attrs in update_uofs_attrs[i:i + BATCH_SIZE]]
            UseOfForce.objects.bulk_update(update_objects, self.UPDATE_ATTRIBUTES)

        return {
            'created_rows': len(new_uofs_attrs),
            'updated_rows': len(update_uofs_attrs),
            'deleted_rows': delete_uofs_count,
        }
