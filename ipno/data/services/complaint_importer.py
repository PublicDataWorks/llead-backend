from tqdm import tqdm

from complaints.models import Complaint
from data.services.base_importer import BaseImporter
from data.constants import COMPLAINT_MODEL_NAME

BATCH_SIZE = 1000


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

    def update_relations(self, complaints):
        DepartmentRelation = Complaint.departments.through
        OfficerRelation = Complaint.officers.through
        department_relation_ids = {}
        officer_relation_ids = {}

        officer_mappings = self.officer_mappings()
        agencies = {complaint.agency for complaint in complaints if complaint.agency}
        department_mappings = self.department_mappings(agencies)

        for complaint in tqdm(complaints):
            officer_uid = complaint.officer_uid
            agency = complaint.agency

            if agency:
                formatted_agency = self.format_agency(agency)
                department_id = department_mappings.get(formatted_agency)
                department_relation_ids[complaint.id] = department_id

            if officer_uid:
                officer_id = officer_mappings.get(officer_uid)
                if officer_id:
                    officer_relation_ids[complaint.id] = officer_id

        department_relations = [
            DepartmentRelation(complaint_id=complaint_id, department_id=department_id)
            for complaint_id, department_id in department_relation_ids.items()
        ]

        officer_relations = [
            OfficerRelation(complaint_id=complaint_id, officer_id=officer_id)
            for complaint_id, officer_id in officer_relation_ids.items()
        ]

        DepartmentRelation.objects.all().delete()
        DepartmentRelation.objects.bulk_create(department_relations, batch_size=BATCH_SIZE)

        OfficerRelation.objects.all().delete()
        OfficerRelation.objects.bulk_create(officer_relations, batch_size=BATCH_SIZE)

    def import_data(self, data):
        new_complaints = []
        update_complaints = []
        new_complaint_uids = []

        complaint_mappings = self.complaint_mappings()

        for row in tqdm(data):
            complaint_data = self.parse_row_data(row)
            complaint_uid = complaint_data['complaint_uid']
            allegation_uid = complaint_data['allegation_uid']
            charge_uid = complaint_data['charge_uid']

            uniq_key = f'{complaint_uid}-{allegation_uid}-{charge_uid}'
            complaint_id = complaint_mappings.get(uniq_key)

            complaint = Complaint(**complaint_data)
            officer_uid = row['uid']
            agency = row['agency']
            setattr(complaint, 'officer_uid', officer_uid)
            setattr(complaint, 'agency', agency)

            if complaint_id:
                complaint.id = complaint_id
                update_complaints.append(complaint)
            elif uniq_key not in new_complaint_uids:
                new_complaints.append(complaint)
                new_complaint_uids.append(uniq_key)

        update_complaint_ids = [complaint.id for complaint in update_complaints]
        delete_complaints = Complaint.objects.exclude(id__in=update_complaint_ids)
        delete_complaints_count = delete_complaints.count()
        delete_complaints.delete()

        created_complaints = Complaint.objects.bulk_create(new_complaints, batch_size=BATCH_SIZE)
        Complaint.objects.bulk_update(update_complaints, self.UPDATE_ATTRIBUTES, batch_size=BATCH_SIZE)

        self.update_relations(created_complaints + update_complaints)

        return {
            'created_rows': len(new_complaints),
            'updated_rows': len(update_complaints),
            'deleted_rows': delete_complaints_count,
        }
