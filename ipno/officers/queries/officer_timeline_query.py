from officers.serializers.officer_timeline_serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer,
    RankChangeTimelineSerializer
)


class OfficerTimelineQuery(object):
    def __init__(self, officer):
        self.officer = officer

    @staticmethod
    def _filter_history_changes(officer_histories, filter_field, compared_field):
        have_year_histories = [
            history for history in officer_histories
            if getattr(history, filter_field)
        ]
        no_year_histories = [
            history for history in officer_histories
            if not getattr(history, filter_field)
        ]

        previous_value = None
        changes = []

        for history in have_year_histories:
            compared_value = getattr(history, compared_field)
            if compared_value != previous_value:
                changes.append(history)
                previous_value = compared_value

        previous_value = None
        for history in no_year_histories:
            compared_value = getattr(history, compared_field)
            if compared_value != previous_value:
                changes.append(history)
                previous_value = compared_value

        return changes

    @property
    def _complaint_timeline(self):
        complaint_timeline_queryset = self.officer.complaint_set.all()

        return ComplaintTimelineSerializer(complaint_timeline_queryset, many=True).data

    @property
    def _join_timeline(self):
        joined_timeline_query = self.officer.officerhistory_set.filter(
            start_date__isnull=False
        )

        return JoinedTimelineSerializer(joined_timeline_query, many=True).data

    @property
    def _left_timeline(self):
        left_timeline_query = self.officer.officerhistory_set.filter(
            end_date__isnull=False
        )

        return LeftTimelineSerializer(left_timeline_query, many=True).data

    @property
    def _document_timeline(self):
        document_timeline_queryset = self.officer.document_set.prefetch_departments()

        return DocumentTimelineSerializer(document_timeline_queryset, many=True).data

    @property
    def _salary_change_timeline(self):
        officer_histories = list(
            self.officer.officerhistory_set.filter(
                annual_salary__isnull=False,
            ).order_by(
                'pay_effective_year',
                'pay_effective_month',
                'pay_effective_day',
                'annual_salary'
            )
        )

        salary_changes = self._filter_history_changes(
            officer_histories,
            'pay_effective_year',
            'annual_salary'
        )

        return SalaryChangeTimelineSerializer(salary_changes, many=True).data

    @property
    def _rank_change_timeline(self):
        officer_histories = list(
            self.officer.officerhistory_set.filter(
                rank_desc__isnull=False,
                rank_code__isnull=False,
            ).order_by(
                'rank_year',
                'rank_month',
                'rank_day',
                'rank_code'
            )
        )

        rank_changes = self._filter_history_changes(officer_histories, 'rank_year', 'rank_code')

        return RankChangeTimelineSerializer(rank_changes, many=True).data

    def query(self):
        return self._complaint_timeline + self._join_timeline + self._left_timeline \
               + self._document_timeline + self._salary_change_timeline + self._rank_change_timeline
