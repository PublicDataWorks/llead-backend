from tqdm import tqdm

from complaints.models import Complaint
from data.services.base_importer import BaseImporter
from data.constants import COMPLAINT_MODEL_NAME


class ComplaintImporter(BaseImporter):
    data_model = COMPLAINT_MODEL_NAME
    ATTRIBUTES = [
        'complaint_uid',
        'allegation_uid',
        'charge_uid',
        'tracking_number',
        'investigation_type',
        'investigation_status',
        'assigned_unit',
        'assigned_department',
        'assigned_division',
        'assigned_sub_division_a',
        'body_worn_camera_available',
        'app_used',
        'citizen_arrested',
        'allegation_finding',
        'allegation',
        'allegation_class',
        'citizen',
        'disposition',
        'rule_code',
        'rule_violation',
        'paragraph_code',
        'paragraph_violation',
        'charges',
        'complainant_name',
        'complainant_type',
        'complainant_sex',
        'complainant_race',
        'recommended_action',
        'action',
        'incident_type',
        'supervisor_uid',
        'supervisor_rank',
        'badge_no',
        'department_code',
        'department_desc',
        'rank_desc',
        'employment_status',
    ]

    INT_ATTRIBUTES = [
        'data_production_year',
    ]

    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES

    def complaint_mappings(self):
        return {
            f'{complaint.complaint_uid}-{complaint.allegation_uid}-{complaint.charge_uid}': complaint.id
            for complaint in Complaint.objects.only('id', 'complaint_uid', 'allegation_uid', 'charge_uid')
        }

    def update_relations(self, data):
        DepartmentRelation = Complaint.departments.through
        OfficerRelation = Complaint.officers.through
        department_relation_ids = {}
        officer_relation_ids = {}

        officer_mappings = self.officer_mappings()
        agencies = {row['agency'] for row in data if row['agency']}
        department_mappings = self.department_mappings(agencies)

        complaint_mappings = self.complaint_mappings()

        for row in tqdm(data):
            officer_uid = row['uid']
            agency = row['agency']

            if officer_uid or agency:
                complaint_uid = row['complaint_uid'] if row['complaint_uid'] else None
                allegation_uid = row['allegation_uid'] if row['allegation_uid'] else None
                charge_uid = row['charge_uid'] if row['charge_uid'] else None

                uniq_key = f'{complaint_uid}-{allegation_uid}-{charge_uid}'
                complaint_id = complaint_mappings.get(uniq_key)

                if complaint_id:
                    if officer_uid:
                        officer_id = officer_mappings.get(officer_uid)
                        if officer_id:
                            officer_relation_ids[complaint_id] = officer_id

                    if agency:
                        formatted_agency = self.format_agency(agency)
                        department_id = department_mappings.get(formatted_agency)

                        department_relation_ids[complaint_id] = department_id

        department_relations = [
            DepartmentRelation(complaint_id=complaint_id, department_id=department_id)
            for complaint_id, department_id in department_relation_ids.items()
        ]

        officer_relations = [
            OfficerRelation(complaint_id=complaint_id, officer_id=officer_id)
            for complaint_id, officer_id in officer_relation_ids.items()
        ]

        DepartmentRelation.objects.all().delete()
        DepartmentRelation.objects.bulk_create(department_relations, batch_size=self.BATCH_SIZE)

        OfficerRelation.objects.all().delete()
        OfficerRelation.objects.bulk_create(officer_relations, batch_size=self.BATCH_SIZE)

    def import_data(self, data):
        new_complaints_attrs = []
        update_complaints_attrs = []
        new_complaint_uids = []

        complaint_mappings = self.complaint_mappings()

        for row in tqdm(data):
            complaint_data = self.parse_row_data(row)
            complaint_uid = complaint_data['complaint_uid']
            allegation_uid = complaint_data['allegation_uid']
            charge_uid = complaint_data['charge_uid']

            uniq_key = f'{complaint_uid}-{allegation_uid}-{charge_uid}'
            complaint_id = complaint_mappings.get(uniq_key)

            if complaint_id:
                complaint_data['id'] = complaint_id
                update_complaints_attrs.append(complaint_data)
            elif uniq_key not in new_complaint_uids:
                new_complaints_attrs.append(complaint_data)
                new_complaint_uids.append(uniq_key)

        import_result = self.bulk_import(Complaint, new_complaints_attrs, update_complaints_attrs)
        self.update_relations(data)
        return import_result