from tqdm import tqdm

from officers.models import Event
from complaints.models import Complaint
from data.services.base_importer import BaseImporter
from data.constants import EVENT_MODEL_NAME


class EventImporter(BaseImporter):
    data_model = EVENT_MODEL_NAME

    ATTRIBUTES = [
        'event_uid',
        'kind',

        'time',
        'raw_date',
        'complaint_uid',
        'appeal_uid',
        'badge_no',
        'employee_id',
        'department_code',
        'department_desc',
        'division_desc',
        'sub_division_a_desc',
        'sub_division_b_desc',
        'current_supervisor',
        'employee_class',
        'rank_code',
        'rank_desc',
        'employment_status',
        'sworn',
        'event_inactive',
        'employee_type',

        'salary',
        'salary_freq',
        'award',
        'award_comments',
    ]
    INT_ATTRIBUTES = [
        'year',
        'month',
        'day',
        'years_employed',
    ]
    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + [
        'officer_id',
        'department_id',
        'use_of_force_id'
    ]

    def event_mappings(self):
        return {event.event_uid: event.id for event in Event.objects.only('id', 'event_uid')}

    def update_relations(self):
        ComplaintRelation = Event.complaints.through
        complaint_relations = []

        events = Event.objects.filter(complaint_uid__isnull=False).only('id', 'complaint_uid')

        for event in tqdm(events):
            complaint_ids = Complaint.objects.filter(
                complaint_uid=event.complaint_uid,
            ).values_list('id', flat=True)

            complaint_relations += [
                ComplaintRelation(complaint_id=complaint_id, event_id=event.id)
                for complaint_id in complaint_ids
            ]

        ComplaintRelation.objects.all().delete()
        ComplaintRelation.objects.bulk_create(complaint_relations, batch_size=self.BATCH_SIZE)

    def import_data(self, data):
        new_events_attrs = []
        update_events_attrs = []
        new_event_uids = []

        agencies = {row['agency'] for row in data if row['agency']}
        department_mappings = self.department_mappings(agencies)

        officer_mappings = self.officer_mappings()
        event_mappings = self.event_mappings()
        uof_mappings = self.uof_mappings()

        for row in tqdm(data):
            agency = row['agency']
            event_uid = row['event_uid']
            officer_uid = row['uid']
            uof_uid = row['uof_uid']

            officer_id = officer_mappings.get(officer_uid)
            uof_id = uof_mappings.get(uof_uid)

            event_data = self.parse_row_data(row)
            formatted_agency = self.format_agency(agency)
            department_id = department_mappings.get(formatted_agency)
            event_data['department_id'] = department_id

            event_data['use_of_force_id'] = uof_id
            event_data['officer_id'] = officer_id

            event_id = event_mappings.get(event_uid)

            if event_id:
                event_data['id'] = event_id
                update_events_attrs.append(event_data)
            elif event_uid not in new_event_uids:
                new_event_uids.append(event_uid)
                new_events_attrs.append(event_data)

        import_result = self.bulk_import(Event, new_events_attrs, update_events_attrs)

        self.update_relations()

        return import_result