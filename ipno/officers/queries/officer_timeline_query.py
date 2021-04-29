from django.db.models import Prefetch, Q

from officers.serializers.officer_timeline_serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer,
    RankChangeTimelineSerializer,
    UnitChangeTimelineSerializer
)
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    COMPLAINT_RECEIVE,
    OFFICER_DEPT
)
from officers.models import Event
from utils.data_utils import sort_items


class OfficerTimelineQuery(object):
    def __init__(self, officer):
        self.officer = officer

    @staticmethod
    def _filter_event_changes(events, compared_fields):
        sorted_events = sort_items(
            events,
            ['year', 'month', 'day'] + compared_fields
        )
        have_year_events = [event for event in sorted_events if event.year]
        no_year_events = [event for event in sorted_events if not event.year]

        previous_event = None
        previous_value = None
        changes = []

        for event in have_year_events:
            compared_value = [getattr(event, compared_field) for compared_field in compared_fields]

            if compared_value != previous_value:
                if previous_event:
                    for field in compared_fields:
                        setattr(event, f'prev_{field}', getattr(previous_event, field))
                changes.append(event)
                previous_event = event
                previous_value = compared_value

        previous_value = None
        for event in no_year_events:
            compared_value = [getattr(event, compared_field) for compared_field in compared_fields]
            if compared_value != previous_value:
                changes.append(event)
                previous_value = compared_value

        return changes

    @property
    def _complaint_timeline(self):
        complaint_timeline_queryset = self.officer.complaint_set.filter(
            allegation_finding__icontains='sustained'
        ).prefetch_related(
            Prefetch(
                'events',
                queryset=Event.objects.filter(kind=COMPLAINT_RECEIVE),
                to_attr='prefetched_receive_events'
            ),
        )

        return ComplaintTimelineSerializer(complaint_timeline_queryset, many=True).data

    @property
    def _join_timeline(self):
        joined_timeline_query = self.officer.event_set.filter(
            kind=OFFICER_HIRE
        )

        return JoinedTimelineSerializer(joined_timeline_query, many=True).data

    @property
    def _left_timeline(self):
        left_timeline_query = self.officer.event_set.filter(
            kind=OFFICER_LEFT
        )

        return LeftTimelineSerializer(left_timeline_query, many=True).data

    @property
    def _document_timeline(self):
        document_timeline_queryset = self.officer.document_set.prefetch_departments()

        return DocumentTimelineSerializer(document_timeline_queryset, many=True).data

    @property
    def _salary_change_timeline(self):
        events = list(
            self.officer.event_set.filter(
                kind=OFFICER_PAY_EFFECTIVE,
            ).filter(
                Q(annual_salary__isnull=False) | Q(hourly_salary__isnull=False),
            )
        )

        salary_changes = self._filter_event_changes(
            events,
            ['annual_salary', 'hourly_salary']
        )

        return SalaryChangeTimelineSerializer(salary_changes, many=True).data

    @property
    def _rank_change_timeline(self):
        events = list(
            self.officer.event_set.filter(
                kind=OFFICER_RANK,
            ).filter(
                Q(rank_code__isnull=False) | Q(rank_desc__isnull=False),
            )
        )

        rank_changes = self._filter_event_changes(
            events,
            ['rank_code', 'rank_desc']
        )

        return RankChangeTimelineSerializer(rank_changes, many=True).data

    @property
    def _unit_change_timeline(self):
        events = self.officer.event_set.filter(
                kind=OFFICER_DEPT
            ).filter(
                Q(department_code__isnull=False) | Q(department_desc__isnull=False),
            )

        unit_changes = self._filter_event_changes(
            events,
            ['department_code', 'department_desc'],
        )

        return UnitChangeTimelineSerializer(unit_changes, many=True).data

    def query(self):
        return self._complaint_timeline + self._join_timeline + self._left_timeline \
               + self._document_timeline + self._salary_change_timeline + self._rank_change_timeline \
               + self._unit_change_timeline
