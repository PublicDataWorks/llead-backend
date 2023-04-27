from datetime import date

from django.test import TestCase

from appeals.factories import AppealFactory
from brady.factories.brady_factory import BradyFactory
from citizens.factory import CitizenFactory
from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory, OfficerMovementFactory
from documents.factories import DocumentFactory
from news_articles.factories import NewsArticleFactory
from officers.constants import (
    APPEAL_TIMELINE_KIND,
    BRADY_LIST,
    BRADY_LIST_TIMELINE_KIND,
    COMPLAINT_RECEIVE,
    COMPLAINT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    FIREARM_CERTIFICATION_TIMELINE_KIND,
    JOINED_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    NEWS_ARTICLE_TIMELINE_KIND,
    OFFICER_DEPT,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_LEVEL_1_CERT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_PC_12_QUALIFICATION,
    OFFICER_POST_DECERTIFICATION,
    OFFICER_RANK,
    PC_12_QUALIFICATION_TIMELINE_KIND,
    POST_DECERTIFICATION_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    RESIGNED_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    TERMINATED_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    UOF_TIMELINE_KIND,
)
from officers.factories import EventFactory, OfficerFactory
from officers.serializers import (
    ComplaintTimelineSerializer,
    DocumentTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    RankChangeTimelineSerializer,
    SalaryChangeTimelineSerializer,
    UnitChangeTimelineSerializer,
    UseOfForceTimelineSerializer,
)
from officers.serializers.officer_timeline_serializers import (
    AppealTimelineSerializer,
    BaseTimelineSerializer,
    BradyTimelineSerializer,
    FirearmTimelineSerializer,
    NewsArticleTimelineSerializer,
    PC12QualificationTimelineSerializer,
    PostDecertificationTimelineSerializer,
    ResignLeftTimelineSerializer,
    TerminatedLeftTimelineSerializer,
)
from people.factories import PersonFactory
from use_of_forces.factories import UseOfForceFactory


class JoinedTimelineSerializerTestCase(TestCase):
    def test_data(self):
        start_department = DepartmentFactory()
        end_department = DepartmentFactory()
        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)

        officer_movement = OfficerMovementFactory(
            start_department=start_department,
            end_department=end_department,
            officer=officer_1,
        )

        EventFactory(
            officer=officer_1,
            department=start_department,
            kind=OFFICER_LEFT,
            year=2018,
            month=1,
            day=8,
        )

        event = EventFactory(
            officer=officer_1,
            department=end_department,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )

        result = JoinedTimelineSerializer(event).data

        assert result == {
            "kind": JOINED_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
            "department": end_department.agency_name,
            "left_department": start_department.agency_name,
            "left_date": str(date(2018, 1, 8)),
            "left_reason": officer_movement.left_reason,
        }

    def test_data_with_only_year(self):
        start_department = DepartmentFactory()
        end_department = DepartmentFactory()
        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)

        officer_movement = OfficerMovementFactory(
            start_department=start_department,
            end_department=end_department,
            officer=officer_1,
        )

        EventFactory(
            officer=officer_1,
            department=start_department,
            kind=OFFICER_LEFT,
            year=2018,
            month=1,
            day=8,
        )

        event = EventFactory(
            officer=officer_1,
            department=end_department,
            kind=OFFICER_HIRE,
            year=2018,
            month=None,
            day=None,
        )

        result = JoinedTimelineSerializer(event).data

        assert result == {
            "kind": JOINED_TIMELINE_KIND,
            "date": None,
            "year": 2018,
            "department": event.department.agency_name,
            "left_department": start_department.agency_name,
            "left_date": str(date(2018, 1, 8)),
            "left_reason": officer_movement.left_reason,
        }

    def test_data_with_empty_date(self):
        start_department = DepartmentFactory()
        end_department = DepartmentFactory()
        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)

        officer_movement = OfficerMovementFactory(
            start_department=start_department,
            end_department=end_department,
            officer=officer_1,
        )

        EventFactory(
            officer=officer_1,
            department=start_department,
            kind=OFFICER_LEFT,
            year=2018,
            month=1,
            day=8,
        )

        event = EventFactory(
            officer=officer_1,
            department=end_department,
            kind=OFFICER_HIRE,
            year=None,
            month=None,
            day=None,
        )

        result = JoinedTimelineSerializer(event).data

        assert result == {
            "kind": JOINED_TIMELINE_KIND,
            "date": None,
            "year": None,
            "department": event.department.agency_name,
            "left_department": start_department.agency_name,
            "left_date": str(date(2018, 1, 8)),
            "left_reason": officer_movement.left_reason,
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
            "kind": LEFT_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
            "department": event.department.agency_name,
        }


class TerminatedTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_LEFT,
            year=2018,
            month=4,
            day=8,
        )

        result = TerminatedLeftTimelineSerializer(event).data

        assert result == {
            "kind": TERMINATED_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
            "department": event.department.agency_name,
        }


class ResignTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_LEFT,
            year=2018,
            month=4,
            day=8,
        )

        result = ResignLeftTimelineSerializer(event).data

        assert result == {
            "kind": RESIGNED_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
            "department": event.department.agency_name,
        }


class ComplaintTimelineSerializerTestCase(TestCase):
    def test_data(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        complaint = ComplaintFactory(tracking_id="0bef1fd2445c53343f9928085acaa34d")
        complaint.officers.add(officer_1)

        other_complaint = ComplaintFactory(
            tracking_id="0bef1fd2445c53343f9928085acaa34d"
        )
        other_complaint.officers.add(officer_2)
        other_complaint.officers.add(officer_3)

        event = EventFactory(
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        setattr(complaint, "prefetched_receive_events", [event])

        result = ComplaintTimelineSerializer(complaint).data

        assert result == {
            "id": complaint.id,
            "kind": COMPLAINT_TIMELINE_KIND,
            "date": str(date(2019, 5, 4)),
            "year": 2019,
            "disposition": complaint.disposition,
            "allegation": complaint.allegation,
            "allegation_desc": complaint.allegation_desc,
            "action": complaint.action,
            "tracking_id": complaint.tracking_id,
            "associated_officers": [
                {
                    "id": officer_2.id,
                    "name": officer_2.name,
                },
                {
                    "id": officer_3.id,
                    "name": officer_3.name,
                },
            ],
        }

    def test_data_with_empty_date(self):
        complaint = ComplaintFactory()
        setattr(complaint, "prefetched_receive_events", [])

        result = ComplaintTimelineSerializer(complaint).data

        assert result == {
            "id": complaint.id,
            "kind": COMPLAINT_TIMELINE_KIND,
            "date": None,
            "year": None,
            "disposition": complaint.disposition,
            "allegation": complaint.allegation,
            "allegation_desc": complaint.allegation_desc,
            "action": complaint.action,
            "tracking_id": complaint.tracking_id,
            "associated_officers": [],
        }


class UseOfForceTimelineSerializerTestCase(TestCase):
    def test_data(self):
        use_of_force = UseOfForceFactory()
        citizen = CitizenFactory(use_of_force=use_of_force)
        EventFactory(
            year=2019,
            month=5,
            day=4,
            use_of_force=use_of_force,
        )

        result = UseOfForceTimelineSerializer(use_of_force).data
        assert result == {
            "id": use_of_force.id,
            "kind": UOF_TIMELINE_KIND,
            "date": str(date(2019, 5, 4)),
            "year": 2019,
            "use_of_force_description": use_of_force.use_of_force_description,
            "use_of_force_reason": use_of_force.use_of_force_reason,
            "disposition": use_of_force.disposition,
            "service_type": use_of_force.service_type,
            "citizen_information": [
                str(citizen.citizen_age)
                + "-year-old "
                + citizen.citizen_race
                + " "
                + citizen.citizen_sex
            ],
            "tracking_id": use_of_force.tracking_id,
            "citizen_arrested": [citizen.citizen_arrested],
            "citizen_injured": [citizen.citizen_injured],
            "citizen_hospitalized": [citizen.citizen_hospitalized],
            "officer_injured": use_of_force.officer_injured,
        }

    def test_data_with_empty_date(self):
        use_of_force = UseOfForceFactory()
        citizen = CitizenFactory(use_of_force=use_of_force)
        result = UseOfForceTimelineSerializer(use_of_force).data

        assert result == {
            "id": use_of_force.id,
            "kind": UOF_TIMELINE_KIND,
            "date": None,
            "year": None,
            "use_of_force_description": use_of_force.use_of_force_description,
            "use_of_force_reason": use_of_force.use_of_force_reason,
            "disposition": use_of_force.disposition,
            "service_type": use_of_force.service_type,
            "citizen_information": [
                str(citizen.citizen_age)
                + "-year-old "
                + citizen.citizen_race
                + " "
                + citizen.citizen_sex
            ],
            "tracking_id": use_of_force.tracking_id,
            "citizen_arrested": [citizen.citizen_arrested],
            "citizen_injured": [citizen.citizen_injured],
            "citizen_hospitalized": [citizen.citizen_hospitalized],
            "officer_injured": use_of_force.officer_injured,
        }


class AppealTimelineSerializerTestCase(TestCase):
    def test_data(self):
        appeal = AppealFactory()
        EventFactory(
            year=2019,
            month=5,
            day=4,
            appeal=appeal,
        )

        result = AppealTimelineSerializer(appeal).data
        assert result == {
            "id": appeal.id,
            "kind": APPEAL_TIMELINE_KIND,
            "date": str(date(2019, 5, 4)),
            "year": 2019,
            "charging_supervisor": appeal.charging_supervisor,
            "appeal_disposition": appeal.appeal_disposition,
            "action_appealed": appeal.action_appealed,
            "motions": appeal.motions,
            "department": appeal.department.agency_name,
        }

    def test_data_with_empty_date(self):
        appeal = AppealFactory()
        result = AppealTimelineSerializer(appeal).data

        assert result == {
            "id": appeal.id,
            "kind": APPEAL_TIMELINE_KIND,
            "date": None,
            "year": None,
            "charging_supervisor": appeal.charging_supervisor,
            "appeal_disposition": appeal.appeal_disposition,
            "action_appealed": appeal.action_appealed,
            "motions": appeal.motions,
            "department": appeal.department.agency_name,
        }


class DocumentTimelineSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory(text_content="Text content")
        department = DepartmentFactory()
        document.departments.add(department)

        result = DocumentTimelineSerializer(document).data

        assert result == {
            "kind": DOCUMENT_TIMELINE_KIND,
            "date": str(document.incident_date),
            "year": document.incident_date.year,
            "id": document.id,
            "document_type": document.document_type,
            "title": document.title,
            "url": document.url,
            "preview_image_url": document.preview_image_url,
            "incident_date": str(document.incident_date),
            "pages_count": document.pages_count,
            "departments": [
                {
                    "id": department.agency_slug,
                    "name": department.agency_name,
                },
            ],
        }


class SalaryChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_PAY_EFFECTIVE,
            salary="57000.15",
            salary_freq="yearly",
            year=2019,
            month=12,
            day=1,
        )

        result = SalaryChangeTimelineSerializer(event).data

        assert result == {
            "kind": SALARY_CHANGE_TIMELINE_KIND,
            "salary": "57000.15",
            "salary_freq": "yearly",
            "date": str(date(2019, 12, 1)),
            "year": 2019,
        }


class RankChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_RANK,
            rank_code="3",
            rank_desc="senior police office",
            year=2017,
            month=7,
            day=13,
        )

        result = RankChangeTimelineSerializer(event).data

        assert result == {
            "kind": RANK_CHANGE_TIMELINE_KIND,
            "rank_code": "3",
            "rank_desc": "senior police office",
            "date": str(date(2017, 7, 13)),
            "year": 2017,
        }


class UnitChangeTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_DEPT,
            department_code="610",
            department_desc="Detective Area - Central",
            year=2017,
            month=7,
            day=13,
        )
        setattr(event, "prev_department_code", "193")
        setattr(event, "prev_department_desc", "Gang Investigation Division")

        result = UnitChangeTimelineSerializer(event).data

        assert result == {
            "kind": UNIT_CHANGE_TIMELINE_KIND,
            "department_code": "610",
            "department_desc": "Detective Area - Central",
            "prev_department_code": "193",
            "prev_department_desc": "Gang Investigation Division",
            "date": str(date(2017, 7, 13)),
            "year": 2017,
        }


class NewsArticleTimelineSerializerTestCase(TestCase):
    def test_data(self):
        news_article = NewsArticleFactory()

        result = NewsArticleTimelineSerializer(news_article).data

        assert result == {
            "kind": NEWS_ARTICLE_TIMELINE_KIND,
            "date": str(news_article.published_date),
            "year": news_article.published_date.year,
            "id": news_article.id,
            "title": news_article.title,
            "url": news_article.url,
            "source_name": news_article.source.source_display_name,
        }


class BaseTimelineSerializerTestCase(TestCase):
    def test_raise_exception(self):
        news_article = NewsArticleFactory()
        with self.assertRaises(NotImplementedError):
            BaseTimelineSerializer(news_article).get_kind(news_article.source)


class PostDecertificationTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_POST_DECERTIFICATION,
            year=2018,
            month=4,
            day=8,
        )
        complaint = ComplaintFactory()
        complaint.events.add(event)

        result = PostDecertificationTimelineSerializer(event).data

        assert result == {
            "id": event.id,
            "kind": POST_DECERTIFICATION_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
            "department": event.department.agency_name,
            "allegations": [complaint.allegation],
        }


class FirearmTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_LEVEL_1_CERT,
            year=2018,
            month=4,
            day=8,
        )

        result = FirearmTimelineSerializer(event).data

        assert result == {
            "kind": FIREARM_CERTIFICATION_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
        }


class PC12QualificationTimelineSerializerTestCase(TestCase):
    def test_data(self):
        event = EventFactory(
            kind=OFFICER_PC_12_QUALIFICATION,
            year=2018,
            month=4,
            day=8,
        )

        result = PC12QualificationTimelineSerializer(event).data

        assert result == {
            "kind": PC_12_QUALIFICATION_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
        }


class BradyTimelineSerializerTestCase(TestCase):
    def test_data(self):
        officer = OfficerFactory()
        department = DepartmentFactory()
        source_department = DepartmentFactory()
        charging_agency = DepartmentFactory()

        brady = BradyFactory(
            department=department,
            source_agency=source_department.agency_slug,
            charging_agency=charging_agency.agency_slug,
            officer=officer,
        )

        EventFactory(
            department=department,
            kind=BRADY_LIST,
            year=2018,
            month=4,
            day=8,
            brady=brady,
        )

        result = BradyTimelineSerializer(brady).data

        assert result == {
            "id": brady.id,
            "kind": BRADY_LIST_TIMELINE_KIND,
            "date": str(date(2018, 4, 8)),
            "year": 2018,
            "department": department.agency_name,
            "source_department": source_department.agency_name,
            "allegation_desc": brady.allegation_desc,
            "action": brady.action,
            "disposition": brady.disposition,
            "charging_department": charging_agency.agency_name,
            "tracking_id_og": brady.tracking_id_og,
        }

    def test_data_with_empty_date(self):
        officer = OfficerFactory()
        department = DepartmentFactory()
        source_department = DepartmentFactory()
        charging_agency = DepartmentFactory()

        brady = BradyFactory(
            department=department,
            source_agency=source_department.agency_slug,
            charging_agency=charging_agency.agency_slug,
            officer=officer,
        )

        result = BradyTimelineSerializer(brady).data

        assert result == {
            "id": brady.id,
            "kind": BRADY_LIST_TIMELINE_KIND,
            "date": None,
            "year": None,
            "department": department.agency_name,
            "source_department": source_department.agency_name,
            "allegation_desc": brady.allegation_desc,
            "action": brady.action,
            "disposition": brady.disposition,
            "charging_department": charging_agency.agency_name,
            "tracking_id_og": brady.tracking_id_og,
        }
