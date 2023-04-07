from datetime import date

from django.db.models import Prefetch
from django.test import TestCase

from complaints.constants import ALLEGATION_DISPOSITION_SUSTAINED
from complaints.factories import ComplaintFactory
from complaints.models import Complaint
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.constants import ALLEGATION_CREATE, COMPLAINT_RECEIVE, UOF_OCCUR
from officers.factories import EventFactory, OfficerFactory
from officers.models import Officer
from officers.serializers import OfficerDetailsSerializer
from people.factories import PersonFactory
from use_of_forces.factories import UseOfForceFactory


class OfficerDetailsSerializerTestCase(TestCase):
    def test_data(self):
        department = DepartmentFactory()

        officer = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            birth_year=1962,
            race="white",
            sex="male",
            department=department,
        )
        person = PersonFactory(
            canonical_officer=officer,
            all_complaints_count=2,
        )
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            department=department,
            badge_no="12435",
            salary="57000.145",
            salary_freq="yearly",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no="67893",
            salary="20.23",
            salary_freq="hourly",
            year=2017,
            month=6,
            day=5,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no="5432",
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            badge_no="12435",
            year=2015,
            month=7,
            day=20,
            department=None,
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4), year=2016)
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4), year=2018)

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        EventFactory(
            officer=officer,
            kind=COMPLAINT_RECEIVE,
            badge_no=None,
            year=2019,
            month=5,
            day=4,
            department=None,
        )
        EventFactory(
            officer=officer,
            kind=ALLEGATION_CREATE,
            badge_no=None,
            year=2020,
            month=5,
            day=4,
            department=None,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer,
            rank_desc="captain",
            year=2021,
            month=None,
            day=None,
        )
        complaint_event = EventFactory(
            department=department,
            officer=officer,
            year=2019,
            month=None,
            day=None,
        )
        sustained_complaint_event = EventFactory(
            department=department,
            officer=officer,
            year=2021,
            month=None,
            day=None,
        )

        complaint_1.events.add(complaint_event)
        complaint_2.events.add(sustained_complaint_event)

        article_1 = NewsArticleFactory(published_date=date(2020, 5, 4))
        matched_sentence_1 = MatchedSentenceFactory(article=article_1)
        matched_sentence_1.officers.add(officer)
        matched_sentence_1.save()
        article_2 = NewsArticleFactory(published_date=date(2021, 5, 4))
        matched_sentence_2 = MatchedSentenceFactory(article=article_2)
        matched_sentence_2.officers.add(officer)
        matched_sentence_2.save()

        uof_incident_event_1 = EventFactory(
            department=department,
            officer=officer,
            kind=UOF_OCCUR,
        )
        uof_1 = UseOfForceFactory(officer=officer)
        uof_1.events.add(uof_incident_event_1)

        EventFactory(
            department=department,
            officer=officer,
            left_reason="termination",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="terminated",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="involuntary termination",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="termination|arrest",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="resigned",
        )
        EventFactory(
            department=department,
            officer=officer,
            award="commendation",
        )

        officer = Officer.objects.filter(person=person).prefetch_related(
            "person__officers__documents",
            "person__officers__matched_sentences",
            "person__officers__events__department",
            "person__officers__events__complaints",
            Prefetch(
                "person__officers__complaints",
                queryset=Complaint.objects.filter(
                    disposition=ALLEGATION_DISPOSITION_SUSTAINED
                ),
                to_attr="sustained_complaints",
            ),
        )[0]

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            "id": officer.id,
            "name": "David Jonesworth",
            "badges": ["12435", "67893", "5432"],
            "birth_year": 1962,
            "race": "white",
            "sex": "male",
            "departments": [
                {
                    "id": department.agency_slug,
                    "name": department.agency_name,
                }
            ],
            "salary": "57000.14",
            "salary_freq": "yearly",
            "documents_count": 3,
            "complaints_count": 2,
            "latest_rank": "captain",
            "articles_count": 2,
            "articles_documents_years": [2016, 2018, 2020, 2021],
            "sustained_complaints_count": 1,
            "complaints_year_count": 2,
            "incident_force_count": 1,
            "termination_count": 4,
            "award_count": 1,
        }

    def test_salary_fields(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            salary="57000.145",
            salary_freq="yearly",
            year=2021,
            month=2,
            day=4,
        )
        EventFactory(
            officer=officer,
            salary=20000.23,
            salary_freq=None,
            year=2020,
            month=1,
            day=2,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq=None,
            year=2021,
            month=3,
            day=6,
        )

        officer = Officer.objects.filter(person=person).prefetch_related(
            "person__officers__documents",
            "person__officers__matched_sentences",
            "person__officers__events__department",
            "person__officers__events__complaints",
            Prefetch(
                "person__officers__complaints",
                queryset=Complaint.objects.filter(
                    disposition=ALLEGATION_DISPOSITION_SUSTAINED
                ),
                to_attr="sustained_complaints",
            ),
        )[0]

        result = OfficerDetailsSerializer(officer).data
        assert result["salary"] == "57000.14"
        assert result["salary_freq"] == "yearly"

    def test_salary_fields_with_empty_salary_freq(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            salary="57000.122",
            salary_freq=None,
            year=2021,
            month=2,
            day=4,
        )
        EventFactory(
            officer=officer,
            salary="20000.152",
            salary_freq=None,
            year=2020,
            month=1,
            day=2,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq=None,
            year=2021,
            month=3,
            day=6,
        )

        officer = Officer.objects.filter(person=person).prefetch_related(
            "person__officers__documents",
            "person__officers__matched_sentences",
            "person__officers__events__department",
            "person__officers__events__complaints",
            Prefetch(
                "person__officers__complaints",
                queryset=Complaint.objects.filter(
                    disposition=ALLEGATION_DISPOSITION_SUSTAINED
                ),
                to_attr="sustained_complaints",
            ),
        )[0]

        result = OfficerDetailsSerializer(officer).data
        assert result["salary"] is None
        assert result["salary_freq"] is None

    def test_salary_fields_with_empty_salary(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        EventFactory(
            officer=officer,
            salary=None,
            salary_freq="yearly",
            year=2021,
            month=2,
            day=4,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq="monthly",
            year=2020,
            month=1,
            day=2,
        )
        EventFactory(
            officer=officer,
            salary=None,
            salary_freq="hourly",
            year=2021,
            month=3,
            day=6,
        )

        officer = Officer.objects.filter(person=person).prefetch_related(
            "person__officers__documents",
            "person__officers__matched_sentences",
            "person__officers__events__department",
            "person__officers__events__complaints",
            Prefetch(
                "person__officers__complaints",
                queryset=Complaint.objects.filter(
                    disposition=ALLEGATION_DISPOSITION_SUSTAINED
                ),
                to_attr="sustained_complaints",
            ),
        )[0]

        result = OfficerDetailsSerializer(officer).data
        assert result["salary"] is None
        assert result["salary_freq"] is None

    def test_officer_data_without_event(self):
        officer = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            birth_year=1962,
            race="white",
            sex="male",
        )
        person = PersonFactory(
            canonical_officer=officer,
            all_complaints_count=2,
        )
        person.officers.add(officer)
        person.save()

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4), year=2016)
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4), year=2017)
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4), year=2018)

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        article_1 = NewsArticleFactory(published_date=date(2020, 5, 4))
        matched_sentence_1 = MatchedSentenceFactory(article=article_1)
        matched_sentence_1.officers.add(officer)
        matched_sentence_1.save()
        article_2 = NewsArticleFactory(published_date=date(2021, 5, 4))
        matched_sentence_2 = MatchedSentenceFactory(article=article_2)
        matched_sentence_2.officers.add(officer)
        matched_sentence_2.save()

        officer = Officer.objects.filter(person=person).prefetch_related(
            "person__officers__documents",
            "person__officers__matched_sentences",
            "person__officers__events__department",
            "person__officers__events__complaints",
            Prefetch(
                "person__officers__complaints",
                queryset=Complaint.objects.filter(
                    disposition=ALLEGATION_DISPOSITION_SUSTAINED
                ),
                to_attr="sustained_complaints",
            ),
        )[0]

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            "id": officer.id,
            "name": "David Jonesworth",
            "badges": [],
            "birth_year": 1962,
            "race": "white",
            "sex": "male",
            "departments": [],
            "salary": None,
            "salary_freq": None,
            "documents_count": 3,
            "complaints_count": 2,
            "latest_rank": None,
            "articles_count": 2,
            "articles_documents_years": [2016, 2017, 2018, 2020, 2021],
            "sustained_complaints_count": 1,
            "complaints_year_count": 0,
            "incident_force_count": 0,
            "termination_count": 0,
            "award_count": 0,
        }

    def test_data_with_related_officer(self):
        department = DepartmentFactory()
        related_department = DepartmentFactory()

        officer = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            birth_year=1962,
            race="white",
            sex="male",
            department=department,
        )
        person = PersonFactory(
            canonical_officer=officer,
            all_complaints_count=2,
        )
        related_officer = OfficerFactory(department=related_department)
        person.officers.add(officer)
        person.officers.add(related_officer)
        person.save()

        EventFactory(
            officer=officer,
            department=department,
            badge_no="12435",
            salary="57000.145",
            salary_freq="yearly",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no="67893",
            salary="20.23",
            salary_freq="hourly",
            year=2017,
            month=6,
            day=10,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no="5432",
            year=2020,
            month=7,
            day=6,
        )
        EventFactory(
            officer=officer,
            badge_no="12435",
            year=2015,
            month=7,
            day=20,
            department=None,
        )
        EventFactory(
            officer=related_officer,
            badge_no="13579",
            year=2021,
            month=7,
            day=20,
            department=related_department,
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4), year=2016)
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4), year=2018)

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(related_officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)

        complaint_1.officers.add(officer)
        complaint_2.officers.add(related_officer)

        EventFactory(
            officer=officer,
            kind=COMPLAINT_RECEIVE,
            badge_no=None,
            year=2019,
            month=5,
            day=4,
            department=None,
        )
        EventFactory(
            officer=officer,
            kind=ALLEGATION_CREATE,
            badge_no=None,
            year=2020,
            month=5,
            day=4,
            department=None,
        )
        complaint_event = EventFactory(
            department=department,
            officer=officer,
            year=2019,
            month=None,
            day=None,
        )
        sustained_complaint_event = EventFactory(
            department=department,
            officer=related_officer,
            year=2021,
            month=None,
            day=None,
        )

        complaint_1.events.add(complaint_event)
        complaint_2.events.add(sustained_complaint_event)

        article_1 = NewsArticleFactory(published_date=date(2020, 5, 4))
        matched_sentence_1 = MatchedSentenceFactory(article=article_1)
        matched_sentence_1.officers.add(officer)
        matched_sentence_1.save()
        article_2 = NewsArticleFactory(published_date=date(2021, 5, 4))
        matched_sentence_2 = MatchedSentenceFactory(article=article_2)
        matched_sentence_2.officers.add(officer)
        matched_sentence_2.save()

        uof_incident_event_1 = EventFactory(
            department=department,
            officer=officer,
            kind=UOF_OCCUR,
        )
        uof_1 = UseOfForceFactory(officer=officer)

        uof_incident_event_2 = EventFactory(
            department=department,
            officer=officer,
            kind=UOF_OCCUR,
        )
        uof_2 = UseOfForceFactory(officer=related_officer)

        uof_1.events.add(uof_incident_event_1)
        uof_2.events.add(uof_incident_event_2)

        EventFactory(
            department=department,
            officer=officer,
            left_reason="termination",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="terminated",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="involuntary termination",
        )
        EventFactory(
            department=department,
            officer=officer,
            left_reason="termination|arrest",
        )
        EventFactory(
            department=department,
            officer=related_officer,
            left_reason="resigned",
        )
        EventFactory(
            department=department,
            officer=officer,
            award="commendation 1",
        )
        EventFactory(
            department=department,
            officer=related_officer,
            award="commendation 2",
        )

        officer = Officer.objects.filter(person=person).prefetch_related(
            "person__officers__documents",
            "person__officers__matched_sentences",
            "person__officers__events__department",
            "person__officers__events__complaints",
            Prefetch(
                "person__officers__complaints",
                queryset=Complaint.objects.filter(
                    disposition=ALLEGATION_DISPOSITION_SUSTAINED
                ),
                to_attr="sustained_complaints",
            ),
        )[0]

        result = OfficerDetailsSerializer(officer).data
        assert result == {
            "id": officer.id,
            "name": "David Jonesworth",
            "badges": ["13579", "5432", "12435", "67893"],
            "birth_year": 1962,
            "race": "white",
            "sex": "male",
            "departments": [
                {
                    "id": department.agency_slug,
                    "name": department.agency_name,
                },
                {
                    "id": related_department.agency_slug,
                    "name": related_department.agency_name,
                },
            ],
            "salary": "57000.14",
            "salary_freq": "yearly",
            "documents_count": 3,
            "complaints_count": 2,
            "latest_rank": None,
            "articles_count": 2,
            "articles_documents_years": [2016, 2018, 2020, 2021],
            "sustained_complaints_count": 1,
            "complaints_year_count": 2,
            "incident_force_count": 2,
            "termination_count": 4,
            "award_count": 2,
        }
