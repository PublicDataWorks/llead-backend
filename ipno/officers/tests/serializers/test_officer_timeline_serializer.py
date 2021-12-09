from datetime import date

from django.test import TestCase

from news_articles.factories import NewsArticleFactory
from officers.serializers import (
    ComplaintTimelineSerializer,
    UseOfForceTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer,
    RankChangeTimelineSerializer,
    UnitChangeTimelineSerializer,
)
from officers.constants import (
    JOINED_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    UOF_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    NEWS_ARTICLE_TIMELINE_KIND,
)
from officers.factories import EventFactory
from complaints.factories import ComplaintFactory
from officers.serializers.officer_timeline_serializers import NewsArticleTimelineSerializer, BaseTimelineSerializer
from use_of_forces.factories import UseOfForceFactory
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    COMPLAINT_RECEIVE,
    OFFICER_DEPT,
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
            'department': event.department.name,
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
            'department': event.department.name,
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
            'department': event.department.name,
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
            'department': event.department.name,
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
            'allegation_desc': complaint.allegation_desc,
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
            'allegation_desc': complaint.allegation_desc,
        }


class UseOfForceTimelineSerializerTestCase(TestCase):
    def test_data(self):
        use_of_force = UseOfForceFactory()
        EventFactory(
            year=2019,
            month=5,
            day=4,
            use_of_force=use_of_force,
        )

        result = UseOfForceTimelineSerializer(use_of_force).data
        assert result == {
            'id': use_of_force.id,
            'kind': UOF_TIMELINE_KIND,
            'date': str(date(2019, 5, 4)),
            'year': 2019,
            'force_type': use_of_force.force_type,
            'force_description': use_of_force.force_description,
            'force_reason': use_of_force.force_reason,
            'disposition': use_of_force.disposition,
            'service_type': use_of_force.service_type,
            'citizen_involvement': use_of_force.citizen_involvement,
            'citizen_age': use_of_force.citizen_age,
            'citizen_race': use_of_force.citizen_race,
            'citizen_sex': use_of_force.citizen_sex,
            'uof_tracking_number': use_of_force.uof_tracking_number,
            'citizen_arrested': use_of_force.citizen_arrested,
            'citizen_injured': use_of_force.citizen_injured,
            'citizen_hospitalized': use_of_force.citizen_hospitalized,
            'officer_injured': use_of_force.officer_injured,
            'traffic_stop': use_of_force.traffic_stop,
        }

    def test_data_with_empty_date(self):
        use_of_force = UseOfForceFactory()
        result = UseOfForceTimelineSerializer(use_of_force).data

        assert result == {
            'id': use_of_force.id,
            'kind': UOF_TIMELINE_KIND,
            'date': None,
            'year': None,
            'force_type': use_of_force.force_type,
            'force_description': use_of_force.force_description,
            'force_reason': use_of_force.force_reason,
            'disposition': use_of_force.disposition,
            'service_type': use_of_force.service_type,
            'citizen_involvement': use_of_force.citizen_involvement,
            'citizen_age': use_of_force.citizen_age,
            'citizen_race': use_of_force.citizen_race,
            'citizen_sex': use_of_force.citizen_sex,
            'uof_tracking_number': use_of_force.uof_tracking_number,
            'citizen_arrested': use_of_force.citizen_arrested,
            'citizen_injured': use_of_force.citizen_injured,
            'citizen_hospitalized': use_of_force.citizen_hospitalized,
            'officer_injured': use_of_force.officer_injured,
            'traffic_stop': use_of_force.traffic_stop,
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
                    'id': department.slug,
                    'name': department.name,
                },
            ],
        }


class SalaryChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_PAY_EFFECTIVE,
            salary='57000.15',
            salary_freq='yearly',
            year=2019,
            month=12,
            day=1,
        )

        result = SalaryChangeTimelineSerializer(event).data

        assert result == {
            'kind': SALARY_CHANGE_TIMELINE_KIND,
            'salary': '57000.15',
            'salary_freq': 'yearly',
            'date': str(date(2019, 12, 1)),
            'year': 2019,
        }


class RankChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_RANK,
            rank_code='3',
            rank_desc='senior police office',
            year=2017,
            month=7,
            day=13,
        )

        result = RankChangeTimelineSerializer(event).data

        assert result == {
            'kind': RANK_CHANGE_TIMELINE_KIND,
            'rank_code': '3',
            'rank_desc': 'senior police office',
            'date': str(date(2017, 7, 13)),
            'year': 2017,
        }


class UnitChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_DEPT,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2017,
            month=7,
            day=13,
        )
        setattr(event, 'prev_department_code', '193')
        setattr(event, 'prev_department_desc', 'Gang Investigation Division')

        result = UnitChangeTimelineSerializer(event).data

        assert result == {
            'kind': UNIT_CHANGE_TIMELINE_KIND,
            'department_code': '610',
            'department_desc': 'Detective Area - Central',
            'prev_department_code': '193',
            'prev_department_desc': 'Gang Investigation Division',
            'date': str(date(2017, 7, 13)),
            'year': 2017,
        }


class NewsArticleTimelineSerializerTestCase(TestCase):
    def test_data(self):
        news_article = NewsArticleFactory()

        result = NewsArticleTimelineSerializer(news_article).data

        assert result == {
            'kind': NEWS_ARTICLE_TIMELINE_KIND,
            'date': str(news_article.published_date),
            'year': news_article.published_date.year,
            'id': news_article.id,
            'title': news_article.title,
            'url': news_article.url,
            'source_name': news_article.source.source_display_name,
        }


class BaseTimelineSerializerTestCase(TestCase):
    def test_raise_exception(self):
        news_article = NewsArticleFactory()
        with self.assertRaises(NotImplementedError):
            BaseTimelineSerializer(news_article).get_kind(news_article.source)
