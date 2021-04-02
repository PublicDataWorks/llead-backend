from officers.serializers.officer_timeline_serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
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

    def query(self):
        return self._complaint_timeline + self._join_timeline + self._left_timeline
