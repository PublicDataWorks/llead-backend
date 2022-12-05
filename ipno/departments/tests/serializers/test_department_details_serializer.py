from datetime import datetime

from django.test import TestCase

import pytz

from complaints.constants import ALLEGATION_DISPOSITION_SUSTAINED
from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory, WrglFileFactory
from departments.serializers import DepartmentDetailsSerializer
from documents.factories import DocumentFactory
from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.constants import OFFICER_HIRE, OFFICER_LEFT, UOF_OCCUR
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory


class DepartmentDetailsSerializerTestCase(TestCase):
    def test_data(self):
        current_date = datetime.now(pytz.utc)

        department = DepartmentFactory(data_period=[2018, 2019, 2020, 2021])
        other_department = DepartmentFactory()

        officer_1 = OfficerFactory(department=department)
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory(department=department)
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()
        officer_3 = OfficerFactory(department=department)
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()
        officer_4 = OfficerFactory(department=other_department)
        person_4 = PersonFactory(canonical_officer=officer_4)
        person_4.officers.add(officer_4)
        person_4.save()

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_OCCUR,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            kind=OFFICER_HIRE,
            year=2018,
            month=5,
            day=8,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=2,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2020,
            month=10,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2020,
            month=12,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_4,
            kind=OFFICER_HIRE,
            year=2017,
            month=2,
            day=3,
        )

        documents = DocumentFactory.create_batch(5)
        DocumentFactory(incident_date=datetime(2018, 8, 10))
        for document in documents:
            document.created_at = datetime(2020, 5, 4, tzinfo=pytz.utc)
            document.departments.add(department)
            document.save()

        recent_documents = DocumentFactory.create_batch(2)
        for document in recent_documents:
            document.created_at = current_date
            document.departments.add(department)
            document.save()

        complaints = ComplaintFactory.create_batch(3)
        ComplaintFactory()
        for complaint in complaints:
            complaint.departments.add(department)

        sustained_complaint = ComplaintFactory(
            disposition=ALLEGATION_DISPOSITION_SUSTAINED
        )
        sustained_complaint.departments.add(department)

        article_1 = NewsArticleFactory(published_date=current_date)
        matched_sentence_1 = MatchedSentenceFactory(
            article=article_1, extracted_keywords=["a"]
        )
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        article_2 = NewsArticleFactory()
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2, extracted_keywords=["b"]
        )
        matched_sentence_2.officers.add(officer_3)
        matched_sentence_2.save()

        wrfile_1 = WrglFileFactory(department=department, position=1)
        wrfile_1.created_at = current_date
        wrfile_1.save()

        wrgl_file_2 = WrglFileFactory(department=department, position=2)
        wrgl_file_2.created_at = datetime(2018, 8, 10, tzinfo=pytz.utc)
        wrgl_file_2.save()

        wrgl_file_3 = WrglFileFactory(department=department, position=3)
        wrgl_file_3.created_at = datetime(2002, 8, 10, tzinfo=pytz.utc)
        wrgl_file_3.save()

        result = DepartmentDetailsSerializer(department).data
        assert result == {
            "id": department.slug,
            "name": department.name,
            "city": department.city,
            "parish": department.parish,
            "phone": department.phone,
            "address": department.address,
            "location_map_url": department.location_map_url,
            "officers_count": 3,
            "datasets_count": 3,
            "recent_datasets_count": 1,
            "news_articles_count": 2,
            "recent_news_articles_count": 1,
            "complaints_count": 4,
            "sustained_complaints_count": 1,
            "documents_count": 7,
            "recent_documents_count": 2,
            "incident_force_count": 2,
            "data_period": ["2018-2021"],
        }

    def test_data_period(self):
        department = DepartmentFactory(
            data_period=[2009, 2012, 2013, 2014, 2016, 2018, 2019, 2020]
        )

        result = DepartmentDetailsSerializer(department).data
        assert result["data_period"] == [
            "2009",
            "2012-2014",
            "2016",
            "2018-2020",
        ]

    def test_data_period_with_empty_data(self):
        department = DepartmentFactory()

        result = DepartmentDetailsSerializer(department).data
        assert result["data_period"] == []

    def test_data_with_related_officer(self):
        current_date = datetime.now(pytz.utc)

        department = DepartmentFactory(data_period=[2018, 2019, 2020, 2021])
        other_department = DepartmentFactory()

        officer_1 = OfficerFactory(department=department)
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory(department=department)
        person_1.officers.add(officer_2)
        person_1.save()
        officer_3 = OfficerFactory(department=department)
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()
        officer_4 = OfficerFactory(department=other_department)
        person_4 = PersonFactory(canonical_officer=officer_4)
        person_4.officers.add(officer_4)
        person_4.save()

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2018,
            month=5,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2019,
            month=5,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_OCCUR,
            year=2018,
            month=7,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            kind=OFFICER_HIRE,
            year=2018,
            month=5,
            day=8,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2020,
            month=5,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2020,
            month=6,
            day=3,
        )

        EventFactory(
            department=other_department,
            officer=officer_4,
            kind=OFFICER_HIRE,
            year=2017,
            month=2,
            day=3,
        )

        documents = DocumentFactory.create_batch(5)
        DocumentFactory(incident_date=datetime(2018, 8, 10))
        for document in documents:
            document.created_at = datetime(2020, 5, 4, tzinfo=pytz.utc)
            document.departments.add(department)
            document.save()

        recent_documents = DocumentFactory.create_batch(2)
        for document in recent_documents:
            document.created_at = current_date
            document.departments.add(department)
            document.save()

        complaints = ComplaintFactory.create_batch(3)
        ComplaintFactory()
        for complaint in complaints:
            complaint.departments.add(department)

        sustained_complaint = ComplaintFactory(
            disposition=ALLEGATION_DISPOSITION_SUSTAINED
        )
        sustained_complaint.departments.add(department)

        article_1 = NewsArticleFactory(published_date=current_date)
        matched_sentence_1 = MatchedSentenceFactory(
            article=article_1, extracted_keywords=["a"]
        )
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        article_2 = NewsArticleFactory()
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2, extracted_keywords=["b"]
        )
        matched_sentence_2.officers.add(officer_2)
        matched_sentence_2.save()

        wrfile_1 = WrglFileFactory(department=department, position=1)
        wrfile_1.created_at = current_date
        wrfile_1.save()

        wrgl_file_2 = WrglFileFactory(department=department, position=2)
        wrgl_file_2.created_at = datetime(2018, 8, 10, tzinfo=pytz.utc)
        wrgl_file_2.save()

        wrgl_file_3 = WrglFileFactory(department=department, position=3)
        wrgl_file_3.created_at = datetime(2002, 8, 10, tzinfo=pytz.utc)
        wrgl_file_3.save()

        result = DepartmentDetailsSerializer(department).data
        assert result == {
            "id": department.slug,
            "name": department.name,
            "city": department.city,
            "parish": department.parish,
            "address": department.address,
            "phone": department.phone,
            "location_map_url": department.location_map_url,
            "officers_count": 2,
            "datasets_count": 3,
            "recent_datasets_count": 1,
            "news_articles_count": 2,
            "recent_news_articles_count": 1,
            "complaints_count": 4,
            "sustained_complaints_count": 1,
            "documents_count": 7,
            "recent_documents_count": 2,
            "incident_force_count": 3,
            "data_period": ["2018-2021"],
        }
