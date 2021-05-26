from tqdm import tqdm

from officers.models import Event
from complaints.models import Complaint
from use_of_forces.models import UseOfForce
from data.services.base_importer import BaseImporter
from data.constants import EVENT_MODEL_NAME


ATTRIBUTES = [
    'event_uid',
    'kind',
    'year',
    'month',
    'day',
    'time',
    'raw_date',
    'complaint_uid',
    'allegation_uid',
    'appeal_uid',
    'badge_no',
    'employee_id',
    'department_code',
    'department_desc',
    'division_desc',
    'sub_division_a_desc',
    'sub_division_b_desc',
    'current_supervisor',
    'rank_code',
    'rank_desc',
    'employment_status',
    'officer_inactive',
    'employee_type',
    'years_employed',
    'salary',
    'salary_freq',
]
UPDATE_ATTRIBUTES = ATTRIBUTES + [
    'officer_id',
    'department_id',
    'use_of_force_id'
]

BATCH_SIZE = 1000


class EventImporter(BaseImporter):
    data_model = EVENT_MODEL_NAME

    def uof_mappings(self):
        return {use_of_force.uof_uid: use_of_force.id for use_of_force in UseOfForce.objects.only('id', 'uof_uid')}

    def update_relations(self):
        ComplaintRelation = Event.complaints.through
        complaint_relations = []

        for event in tqdm(Event.objects.only('id', 'complaint_uid', 'allegation_uid')):
            if event.complaint_uid or event.allegation_uid:
                complaint_ids = Complaint.objects.filter(
                    complaint_uid=event.complaint_uid,
                    allegation_uid=event.allegation_uid,
                ).values_list('id', flat=True)

                complaint_relations += [ComplaintRelation(complaint_id=complaint_id, event_id=event.id) for complaint_id in complaint_ids]

        ComplaintRelation.objects.all().delete()
        ComplaintRelation.objects.bulk_create(complaint_relations, batch_size=BATCH_SIZE)

    def import_data(self, data):
        new_events = []
        update_events = []
        new_event_uids = []

        officer_mappings = self.officer_mappings()
        agencies = {row['agency'] for row in data if row['agency']}
        department_mappings = self.department_mappings(agencies)
        uof_mappings = self.uof_mappings()

        for row in tqdm(data):
            agency = row['agency']
            event_uid = row['event_uid']
            officer_uid = row['uid']
            uof_uid = row['uof_uid']

            formatted_agency = self.format_agency(agency)
            officer_id = officer_mappings.get(officer_uid)
            department_id = department_mappings.get(formatted_agency)
            uof_id = uof_mappings.get(uof_uid)

            event_data = {attr: row[attr] if row[attr] else None for attr in ATTRIBUTES if attr in row}

            event_data['use_of_force_id'] = uof_id
            event_data['department_id'] = department_id
            event_data['officer_id'] = officer_id

            event = Event.objects.filter(
                event_uid=event_uid,
            ).first()

            if event:
                for attr, value in event_data.items():
                    setattr(event, attr, value)
                update_events.append(event)
            elif event_uid not in new_event_uids:
                new_event_uids.append(event_uid)
                new_events.append(
                    Event(**event_data)
                )

        update_event_ids = [event.id for event in update_events]
        delete_events = Event.objects.exclude(id__in=update_event_ids)
        delete_events_count = delete_events.count()
        delete_events.delete()

        Event.objects.bulk_create(new_events, batch_size=BATCH_SIZE)

        Event.objects.bulk_update(update_events, UPDATE_ATTRIBUTES, batch_size=BATCH_SIZE)

        self.update_relations()

        return {
            'created_rows': len(new_events),
            'updated_rows': len(update_events),
            'deleted_rows': delete_events_count,
        }
