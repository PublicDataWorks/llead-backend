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
from officers.factories import OfficerHistoryFactory
from complaints.factories import ComplaintFactory
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory


class JoinedTimelineSerializerTestCase(TestCase):
    def test_data(self):
        officer_history = OfficerHistoryFactory(
            start_date=date(2018, 4, 8),
            hire_year=2018,
        )

        result = JoinedTimelineSerializer(officer_history).data

        assert result == {
            'kind': JOINED_TIMELINE_KIND,
            'date': str(officer_history.start_date),
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
            'kind': LEFT_TIMELINE_KIND,
            'date': str(officer_history.end_date),
            'year': officer_history.term_year,
        }


class ComplaintTimelineSerializerTestCase(TestCase):
    def test_data(self):
        complaint = ComplaintFactory(incident_date=date(2019, 5, 4), )

        result = ComplaintTimelineSerializer(complaint).data

        assert result == {
            'kind': COMPLAINT_TIMELINE_KIND,
            'date': str(complaint.incident_date),
            'year': complaint.occur_year,
            'rule_violation': complaint.rule_violation,
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
        officer_history = OfficerHistoryFactory(
            annual_salary='57k',
            pay_effective_year=2019,
            pay_effective_month=12,
            pay_effective_day=1,

        )

        result = SalaryChangeTimelineSerializer(officer_history).data

        assert result == {
            'kind': SALARY_CHANGE_TIMELINE_KIND,
            'annual_salary': '57k',
            'date': date(2019, 12, 1),
            'year': 2019,
        }


class RankChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        officer_history = OfficerHistoryFactory(
            rank_desc='senior police office',
            rank_year=2017,
            rank_month=7,
            rank_day=13,
        )

        result = RankChangeTimelineSerializer(officer_history).data

        assert result == {
            'kind': RANK_CHANGE_TIMELINE_KIND,
            'rank_desc': 'senior police office',
            'date': date(2017, 7, 13),
            'year': 2017,
        }
