from datetime import date

from django.test import TestCase

from officers.serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
)
from officers.constants import (
    JOINED_TIMELINE_TYPE,
    COMPLAINT_TIMELINE_TYPE,
    LEFT_TIMELINE_TYPE,
)
from officers.factories import OfficerHistoryFactory
from complaints.factories import ComplaintFactory


class JoinedTimelineSerializerTestCase(TestCase):
    def test_data(self):
        officer_history = OfficerHistoryFactory(
            start_date=date(2018, 4, 8),
            hire_year=2018,
        )

        result = JoinedTimelineSerializer(officer_history).data

        assert result == {
            'kind': JOINED_TIMELINE_TYPE,
            'date': officer_history.start_date,
            'year': officer_history.hire_year,
        }


class LeftTimelineSerializerTestCase(TestCase):
    def test_data(self):
        officer_history = OfficerHistoryFactory(
            end_date=date(2020, 4, 8),
            term_year=2020,
        )

        result = LeftTimelineSerializer(officer_history).data

        assert result == {
            'kind': LEFT_TIMELINE_TYPE,
            'date': officer_history.end_date,
            'year': officer_history.term_year,
        }


class ComplaintTimelineSerializerTestCase(TestCase):
    def test_data(self):
        complaint = ComplaintFactory(incident_date=date(2019, 5, 4), )

        result = ComplaintTimelineSerializer(complaint).data

        assert result == {
            'kind': COMPLAINT_TIMELINE_TYPE,
            'date': complaint.incident_date,
            'year': complaint.occur_year,
            'rule_violation': complaint.rule_violation,
            'paragraph_violation': complaint.paragraph_violation,
            'disposition': complaint.disposition,
            'action': complaint.action,
            'tracking_number': complaint.tracking_number,
        }
