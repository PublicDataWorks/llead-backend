from officers.serializers.officer_timeline_serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer,
    RankChangeTimelineSerializer
)
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
)


class OfficerTimelineQuery(object):
    def __init__(self, officer):
        self.officer = officer

    @staticmethod
    def _filter_event_changes(events, compared_field):
        have_year_events = [event for event in events if event.year]
        no_year_events = [event for event in events if not event.year]

        previous_value = None
        changes = []

        for event in have_year_events:
            compared_value = getattr(event, compared_field)
            if compared_value != previous_value:
                changes.append(event)
                previous_value = compared_value

        previous_value = None
        for event in no_year_events:
            compared_value = getattr(event, compared_field)
            if compared_value != previous_value:
                changes.append(event)
                previous_value = compared_value

        return changes

    @property
    def _complaint_timeline(self):
        complaint_timeline_queryset = self.officer.complaint_set.all()

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
                annual_salary__isnull=False,
            ).order_by(
                'year',
                'month',
                'day',
                'annual_salary'
            )
        )

        salary_changes = self._filter_event_changes(
            events,
            'annual_salary'
        )

        return SalaryChangeTimelineSerializer(salary_changes, many=True).data

    @property
    def _rank_change_timeline(self):
        events = list(
            self.officer.event_set.filter(
                kind=OFFICER_RANK,
                rank_code__isnull=False,
            ).order_by(
                'year',
                'month',
                'day',
                'rank_code'
            )
        )

        rank_changes = self._filter_event_changes(events, 'rank_code')

        return RankChangeTimelineSerializer(rank_changes, many=True).data

    def query(self):
        return self._complaint_timeline + self._join_timeline + self._left_timeline \
               + self._document_timeline + self._salary_change_timeline + self._rank_change_timeline
