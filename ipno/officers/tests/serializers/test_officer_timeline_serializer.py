from datetime import date

from django.test import TestCase

from officers.serializers import (
    ComplaintTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer,
    RankChangeTimelineSerializer
)
from officers.constants import (
    JOINED_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND
)
from officers.factories import EventFactory
from complaints.factories import ComplaintFactory
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    COMPLAINT_RECEIVE,
)


class JoinedTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )

        result = JoinedTimelineSerializer(event).data

        assert result == {
            'kind': JOINED_TIMELINE_KIND,
            'date': str(date(2018, 4, 8)),
            'year': 2018,
        }

    def test_data_with_only_year(self):
        event = EventFactory(
            kind=OFFICER_HIRE,
            year=2018,
            month=None,
            day=None,
        )

        result = JoinedTimelineSerializer(event).data

        assert result == {
            'kind': JOINED_TIMELINE_KIND,
            'date': None,
            'year': 2018,
        }

    def test_data_with_empty_date(self):
        event = EventFactory(
            kind=OFFICER_HIRE,
            year=None,
            month=None,
            day=None,
        )

        result = JoinedTimelineSerializer(event).data

        assert result == {
            'kind': JOINED_TIMELINE_KIND,
            'date': None,
            'year': None,
        }


class LeftTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_LEFT,
            year=2018,
            month=4,
            day=8,
        )

        result = LeftTimelineSerializer(event).data

        assert result == {
            'kind': LEFT_TIMELINE_KIND,
            'date': str(date(2018, 4, 8)),
            'year': 2018,
        }


class ComplaintTimelineSerializerTestCase(TestCase):
    def test_data(self):
        complaint = ComplaintFactory()
        event = EventFactory(
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        setattr(complaint, 'prefetched_receive_events', [event])

        result = ComplaintTimelineSerializer(complaint).data

        assert result == {
            'id': complaint.id,
            'kind': COMPLAINT_TIMELINE_KIND,
            'date': str(date(2019, 5, 4)),
            'year': 2019,
            'rule_code': complaint.rule_code,
            'rule_violation': complaint.rule_violation,
            'paragraph_code': complaint.paragraph_code,
            'paragraph_violation': complaint.paragraph_violation,
            'disposition': complaint.disposition,
            'action': complaint.action,
            'tracking_number': complaint.tracking_number,
        }

    def test_data_with_empty_date(self):
        complaint = ComplaintFactory()
        setattr(complaint, 'prefetched_receive_events', [])

        result = ComplaintTimelineSerializer(complaint).data

        assert result == {
            'id': complaint.id,
            'kind': COMPLAINT_TIMELINE_KIND,
            'date': None,
            'year': None,
            'rule_code': complaint.rule_code,
            'rule_violation': complaint.rule_violation,
            'paragraph_code': complaint.paragraph_code,
            'paragraph_violation': complaint.paragraph_violation,
            'disposition': complaint.disposition,
            'action': complaint.action,
            'tracking_number': complaint.tracking_number,
        }


class DocumentTimelineSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory(text_content='Text content')
        department = DepartmentFactory()
        document.departments.add(department)

        result = DocumentTimelineSerializer(document).data

        assert result == {
            'kind': DOCUMENT_TIMELINE_KIND,
            'date': str(document.incident_date),
            'year': document.incident_date.year,
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'preview_image_url': document.preview_image_url,
            'incident_date': str(document.incident_date),
            'pages_count': document.pages_count,
            'departments': [
                {
                    'id': department.id,
                    'name': department.name,
                },
            ],
        }


class SalaryChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='57k',
            year=2019,
            month=12,
            day=1,
        )

        result = SalaryChangeTimelineSerializer(event).data

        assert result == {
            'kind': SALARY_CHANGE_TIMELINE_KIND,
            'annual_salary': '57k',
            'date': str(date(2019, 12, 1)),
            'year': 2019,
        }


class RankChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_RANK,
            rank_desc='senior police office',
            year=2017,
            month=7,
            day=13,
        )

        result = RankChangeTimelineSerializer(event).data

        assert result == {
            'kind': RANK_CHANGE_TIMELINE_KIND,
            'rank_desc': 'senior police office',
            'date': str(date(2017, 7, 13)),
            'year': 2017,
        }
