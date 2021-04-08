from officers.serializers.officer_timeline_serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer
)


class OfficerTimelineQuery(object):
    def __init__(self, officer):
        self.officer = officer

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
        histories = list(
            self.officer.officerhistory_set.filter(
                annual_salary__isnull=False,
            ).order_by(
                'pay_effective_year',
                'pay_effective_month',
                'pay_effective_day',
                'annual_salary'
            )
        )

        have_year_histories = [history for history in histories if history.pay_effective_year]
        no_year_histories = [history for history in histories if not history.pay_effective_year]

        previous_salary = None
        salary_changes = []

        for history in have_year_histories:
            if history.annual_salary != previous_salary:
                salary_changes.append(history)
                previous_salary = history.annual_salary

        previous_salary = None
        for history in no_year_histories:
            if history.annual_salary != previous_salary:
                salary_changes.append(history)
                previous_salary = history.annual_salary

        return SalaryChangeTimelineSerializer(salary_changes, many=True).data

    def query(self):
        return self._complaint_timeline + self._join_timeline + self._left_timeline + self._document_timeline \
               + self._salary_change_timeline
