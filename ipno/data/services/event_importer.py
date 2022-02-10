from itertools import chain

from django.template.defaultfilters import slugify
from tqdm import tqdm

from officers.models import Event
from complaints.models import Complaint
from data.services.base_importer import BaseImporter
from data.constants import EVENT_MODEL_NAME


class EventImporter(BaseImporter):
    data_model = EVENT_MODEL_NAME
    WRGL_OFFSET_BATCH_SIZE = 750

    ATTRIBUTES = [
        'event_uid',
        'kind',

        'time',
        'raw_date',
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

    def __init__(self):
        self.new_events_attrs = []
        self.update_events_attrs = []
        self.new_event_uids = []
        self.delete_events_ids = []
        self.department_mappings = {}
        self.officer_mappings = {}
        self.event_mappings = {}
        self.uof_mappings = {}

    def get_event_mappings(self):
        return {event.event_uid: event.id for event in Event.objects.only('id', 'event_uid')}

    def update_relations(self):
        ComplaintRelation = Event.complaints.through
        complaint_relations = []

        events = Event.objects.filter(allegation_uid__isnull=False).only('id', 'allegation_uid')

        for event in tqdm(events, desc='Update events\' relations'):
            complaint_ids = Complaint.objects.filter(
                allegation_uid=event.allegation_uid,
            ).values_list('id', flat=True)

            complaint_relations += [
                ComplaintRelation(complaint_id=complaint_id, event_id=event.id)
                for complaint_id in complaint_ids
            ]

        ComplaintRelation.objects.all().delete()
        ComplaintRelation.objects.bulk_create(complaint_relations, batch_size=self.BATCH_SIZE)

    def handle_record_data(self, row):
        agency = row[self.column_mappings['agency']]
        event_uid = row[self.column_mappings['event_uid']]
        officer_uid = row[self.column_mappings['uid']]
        uof_uid = row[self.column_mappings['uof_uid']]

        officer_id = self.officer_mappings.get(officer_uid)
        uof_id = self.uof_mappings.get(uof_uid)

        event_data = self.parse_row_data(row, self.column_mappings)
        formatted_agency = self.format_agency(agency)
        department_id = self.department_mappings.get(slugify(formatted_agency))
        event_data['department_id'] = department_id

        event_data['use_of_force_id'] = uof_id
        event_data['officer_id'] = officer_id

        event_id = self.event_mappings.get(event_uid)

        if event_id:
            event_data['id'] = event_id
            self.update_events_attrs.append(event_data)
        elif event_uid not in self.new_event_uids:
            self.new_event_uids.append(event_uid)
            self.new_events_attrs.append(event_data)

    def import_data(self, data):
        saved_data = list(chain(
            data.get('added_rows', []),
            data.get('updated_rows', []),
        ))
        deleted_data = data.get('deleted_rows', [])

        agencies = {row[self.column_mappings['agency']] for row in saved_data if row[self.column_mappings['agency']]}
        agencies.update([
            row[self.old_column_mappings['agency']] for row in deleted_data if row[self.old_column_mappings['agency']]
        ])
        self.department_mappings = self.get_department_mappings(agencies)

        self.officer_mappings = self.get_officer_mappings()
        self.event_mappings = self.get_event_mappings()
        self.uof_mappings = self.get_uof_mappings()

        for row in tqdm(data.get('added_rows'), desc='Create new events'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed events'):
            event_uid = row[self.old_column_mappings['event_uid']]
            event_id = self.event_mappings.get(event_uid)
            if event_id:
                self.delete_events_ids.append(event_id)

        for row in tqdm(data.get('updated_rows'), desc='Update modified events'):
            self.handle_record_data(row)

        import_result = self.bulk_import(Event, self.new_events_attrs, self.update_events_attrs, self.delete_events_ids)

        self.update_relations()

        return import_result
