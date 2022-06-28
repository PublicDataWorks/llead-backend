from unittest.mock import patch

import pytz
from datetime import date, datetime
from operator import itemgetter
from re import findall

from django.urls import reverse
from rest_framework import status

from complaints.constants import ALLEGATION_DISPOSITION_SUSTAINED
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from departments.factories import DepartmentFactory, WrglFileFactory
from officers.factories import EventFactory, OfficerFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from use_of_forces.factories import UseOfForceFactory, UseOfForceOfficerFactory
from utils.parse_utils import parse_date
from utils.search_index import rebuild_search_index
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    UOF_OCCUR,
    UOF_RECEIVE,
)


class DepartmentsViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()
        DepartmentFactory()

        OfficerFactory.create_batch(2, department=department_1)
        OfficerFactory.create_batch(3, department=department_2)

        document = DocumentFactory()
        document.departments.add(department_1)

        UseOfForceFactory(department=department_2)

        complaint = ComplaintFactory()
        complaint.departments.add(department_3)

        EventFactory.create_batch(2, department=department_1)
        EventFactory(department=department_2)

        expected_data = [{
            'id': department_2.slug,
            'name': department_2.name,
            'city': department_2.city,
            'parish': department_2.parish,
            'location_map_url': department_2.location_map_url,
        }, {
            'id': department_1.slug,
            'name': department_1.name,
            'city': department_1.city,
            'parish': department_1.parish,
            'location_map_url': department_1.location_map_url,
        }, {
            'id': department_3.slug,
            'name': department_3.name,
            'city': department_3.city,
            'parish': department_3.parish,
            'location_map_url': department_3.location_map_url,
        }]

        response = self.auth_client.get(reverse('api:departments-list'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self):
        current_date = datetime.now(pytz.utc)
        department = DepartmentFactory()
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

        sustained_complaint = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)
        sustained_complaint.departments.add(department)

        article_1 = NewsArticleFactory(published_date=current_date)
        matched_sentence_1 = MatchedSentenceFactory(
            article=article_1,
            extracted_keywords=['a']
        )
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        article_2 = NewsArticleFactory()
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2,
            extracted_keywords=['b']
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

        expected_result = {
            'id': department.slug,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'address': department.address,
            'phone': department.phone,
            'location_map_url': department.location_map_url,
            'officers_count': 3,
            'datasets_count': 3,
            'recent_datasets_count': 1,
            'news_articles_count': 2,
            'recent_news_articles_count': 1,
            'complaints_count': 4,
            'sustained_complaints_count': 1,
            'documents_count': 7,
            'recent_documents_count': 2,
            'incident_force_count': 2,
            'data_period': department.data_period,
        }

        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': department.slug})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_retrieve_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-detail', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_documents_with_keywords(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(
            title='Document title 1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 4)
        )
        document_2 = DocumentFactory(
            title='Document title keyword3',
            text_content='Text content 3',
            incident_date=date(2019, 11, 6)
        )
        document_3 = DocumentFactory(
            title='Document title keyword 4',
            text_content='Text content keyword 4',
            incident_date=date(2021, 7, 9)
        )

        DocumentFactory(
            title='Document title keyword2',
            text_content='Text content keyword 2',
            incident_date=date(2017, 12, 5)
        )

        for document in [document_1, document_2, document_3]:
            document.departments.add(department)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'keyword',
                'kind': 'documents',
            }
        )

        expected_results = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'preview_image_url': document_2.preview_image_url,
                'pages_count': document_2.pages_count,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    },
                ],
                'text_content': document_2.text_content,
                'text_content_highlight': None,
            }, {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'incident_date': str(document_3.incident_date),
                'preview_image_url': document_3.preview_image_url,
                'pages_count': document_3.pages_count,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    },
                ],
                'text_content': document_3.text_content,
                'text_content_highlight': 'Text content <em>keyword</em> 4',
            }
        ]

        results = sorted(response.data['results'], key=itemgetter('id'))

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert results == expected_results

    def test_search_documents_with_limit_and_offset(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(
            title='Document title 1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 4)
        )
        document_2 = DocumentFactory(
            title='Document title keyword3',
            text_content='Text content 3',
            incident_date=date(2019, 11, 6)
        )
        document_3 = DocumentFactory(
            title='Document title keyword 4',
            text_content='Text content keyword 4',
            incident_date=date(2021, 7, 9)
        )

        DocumentFactory(
            title='Document title keyword2',
            text_content='Text content keyword 2',
            incident_date=date(2017, 12, 5)
        )

        for document in [document_1, document_2, document_3]:
            document.departments.add(department)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'keyword',
                'offset': 1,
                'limit': 1,
                'kind': 'documents',
            }
        )

        expected_results = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'preview_image_url': document_2.preview_image_url,
                'pages_count': document_2.pages_count,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    },
                ],
                'text_content': document_2.text_content,
                'text_content_highlight': None,
            },
        ]

        expected_previous = f'http://testserver/api/departments/{department.slug}/search/?kind=documents&limit=1&q=keyword'

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['previous'] == expected_previous
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_documents_with_empty_results(self):
        department = DepartmentFactory()
        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'keyword',
                'kind': 'documents',
            }
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert response.data['results'] == []

    def test_retrieve_success_with_related_officer(self):
        current_date = datetime.now(pytz.utc)
        department = DepartmentFactory(
            data_period=['20']
        )
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

        sustained_complaint = ComplaintFactory(disposition=ALLEGATION_DISPOSITION_SUSTAINED)
        sustained_complaint.departments.add(department)

        article_1 = NewsArticleFactory(published_date=current_date)
        matched_sentence_1 = MatchedSentenceFactory(
            article=article_1,
            extracted_keywords=['a']
        )
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        article_2 = NewsArticleFactory()
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2,
            extracted_keywords=['b']
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

        expected_result = {
            'id': department.slug,
            'name': department.name,
            'city': department.city,
            'parish': department.parish,
            'address': department.address,
            'phone': department.phone,
            'location_map_url': department.location_map_url,
            'officers_count': 2,
            'datasets_count': 3,
            'recent_datasets_count': 1,
            'news_articles_count': 2,
            'recent_news_articles_count': 1,
            'complaints_count': 4,
            'sustained_complaints_count': 1,
            'documents_count': 7,
            'recent_documents_count': 2,
            'incident_force_count': 3,
            'data_period': department.data_period,
        }

        response = self.auth_client.get(
            reverse('api:departments-detail', kwargs={'pk': department.slug})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_datasets_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-datasets', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_datasets_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-datasets', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_datasets_success(self):
        department = DepartmentFactory()

        wrgl_file_1 = WrglFileFactory(department=department, position=2)
        wrgl_file_2 = WrglFileFactory(department=department, position=1)

        response = self.auth_client.get(
            reverse('api:departments-datasets', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': wrgl_file_2.id,
                'name': wrgl_file_2.name,
                'slug': wrgl_file_2.slug,
                'description': wrgl_file_2.description,
                'url': wrgl_file_2.url,
                'download_url': wrgl_file_2.download_url,
                'default_expanded': wrgl_file_2.default_expanded,
            },
            {
                'id': wrgl_file_1.id,
                'name': wrgl_file_1.name,
                'slug': wrgl_file_1.slug,
                'description': wrgl_file_1.description,
                'url': wrgl_file_1.url,
                'download_url': wrgl_file_1.download_url,
                'default_expanded': wrgl_file_1.default_expanded,
            }
        ]

        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_officers_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-officers', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_officers_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-officers', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_officers_success(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory(department=department)
        officer_2 = OfficerFactory(department=department)
        person_1 = PersonFactory(canonical_officer=officer_2, all_complaints_count=150)
        person_1.officers.add(officer_1)
        person_1.officers.add(officer_2)
        person_1.save()

        officer_3 = OfficerFactory(department=department)
        person_2 = PersonFactory(canonical_officer=officer_3, all_complaints_count=100)
        person_2.officers.add(officer_3)
        person_2.save()

        officer_4 = OfficerFactory(department=department)
        person_3 = PersonFactory(canonical_officer=officer_4, all_complaints_count=110)
        person_3.officers.add(officer_4)
        person_3.save()

        department.starred_officers.add(officer_2)
        department.save()

        use_of_force_1 = UseOfForceFactory()
        use_of_force_2 = UseOfForceFactory()
        use_of_force_3 = UseOfForceFactory()

        UseOfForceOfficerFactory(officer=officer_3, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(officer=officer_2, use_of_force=use_of_force_2)
        UseOfForceOfficerFactory(officer=officer_2, use_of_force=use_of_force_3)

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="150",
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="100",
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="250",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="150",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_2 = EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_RECEIVE,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        uof_incident_event_2 = EventFactory(
            department=department,
            officer=officer_2,
            kind=UOF_OCCUR,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            badge_no="123",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_1 = EventFactory(
            department=department,
            officer=officer_3,
            kind=UOF_RECEIVE,
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_4,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            rank_desc="sergeant",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_4,
            rank_desc="recruit",
            year=2020,
            month=4,
            day=5,
        )

        use_of_force_1.events.add(uof_receive_event_1)
        use_of_force_2.events.add(uof_receive_event_2)
        use_of_force_3.events.add(uof_incident_event_2)

        response = self.auth_client.get(
            reverse('api:departments-officers', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': officer_2.id,
                'name': officer_2.name,
                'is_starred': True,
                'use_of_forces_count': 2,
                'badges': ["150", "200", "100", "250"],
                'complaints_count': officer_2.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'senior',
            },
            {
                'id': officer_4.id,
                'name': officer_4.name,
                'is_starred': False,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': officer_4.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'recruit',
            },
            {
                'id': officer_3.id,
                'name': officer_3.name,
                'is_starred': False,
                'use_of_forces_count': 1,
                'badges': ["123"],
                'complaints_count': officer_3.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'sergeant',
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    @patch('departments.views.DEPARTMENTS_LIMIT', 3)
    def test_officers_with_maximum_starred_officers(self):
        department = DepartmentFactory()
        starred_officers = OfficerFactory.create_batch(3, department=department)
        starred_person = PersonFactory(canonical_officer=starred_officers[0])
        for starred_officer in starred_officers:
            department.starred_officers.add(starred_officer)
            starred_person.officers.add(starred_officer)
        department.save()
        starred_person.save()

        featured_officer = OfficerFactory(department=department)
        featured_person = PersonFactory(canonical_officer=featured_officer)
        featured_person.officers.add(featured_officer)
        featured_person.save()
        department.officers.add(featured_officer)
        department.save()

        response = self.auth_client.get(
            reverse('api:departments-officers', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': starred_officers[0].id,
                'name': starred_officers[0].name,
                'is_starred': True,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': starred_person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': None,
            },
            {
                'id': starred_officers[1].id,
                'name': starred_officers[1].name,
                'is_starred': True,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': starred_person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': None,
            },
            {
                'id': starred_officers[2].id,
                'name': starred_officers[2].name,
                'is_starred': True,
                'use_of_forces_count': 0,
                'badges': [],
                'complaints_count': starred_person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': None,
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    def test_news_articles_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-news-articles', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_news_articles_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-news-articles', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_news_articles_success(self):
        current_date = datetime.now(pytz.utc)
        department = DepartmentFactory()

        officer_1 = OfficerFactory(department=department)
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        starred_article_source = NewsArticleSourceFactory(source_display_name='Starred Article')
        starred_article = NewsArticleFactory(
            source=starred_article_source,
            published_date=datetime(2015, 1, 1),
        )
        starred_matched_sentence = MatchedSentenceFactory(article=starred_article)
        starred_matched_sentence.officers.add(officer_1)
        starred_matched_sentence.save()

        department.starred_news_articles.add(starred_article)
        department.save()

        featured_article_source_1 = NewsArticleSourceFactory(source_display_name='Featured Article 1')
        featured_article_1 = NewsArticleFactory(
            source=featured_article_source_1,
            published_date=current_date,
        )
        matched_sentence_1 = MatchedSentenceFactory(article=featured_article_1)
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_1.save()

        featured_article_source_2 = NewsArticleSourceFactory(source_display_name='Featured Article 2')
        featured_article_2 = NewsArticleFactory(
            source=featured_article_source_2,
            published_date=datetime(2019, 8, 10),
        )
        matched_sentence_2 = MatchedSentenceFactory(article=featured_article_2)
        matched_sentence_2.officers.add(officer_1)
        matched_sentence_2.save()

        featured_article_source_3 = NewsArticleSourceFactory(source_display_name='Featured Article 3')
        featured_article_3 = NewsArticleFactory(
            source=featured_article_source_3,
            published_date=datetime(2018, 8, 10),
        )
        matched_sentence_3 = MatchedSentenceFactory(article=featured_article_3)
        matched_sentence_3.officers.add(officer_1)
        matched_sentence_3.save()

        response = self.auth_client.get(
            reverse('api:departments-news-articles', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': starred_article.id,
                'title': starred_article.title,
                'published_date': str(datetime(2015, 1, 1).date()),
                'source_display_name': 'Starred Article',
                'is_starred': True,
                'url': starred_article.url,
            },
            {
                'id': featured_article_1.id,
                'title': featured_article_1.title,
                'published_date': str(current_date.date()),
                'source_display_name': 'Featured Article 1',
                'is_starred': False,
                'url': featured_article_1.url,
            },
            {
                'id': featured_article_2.id,
                'title': featured_article_2.title,
                'published_date': str(datetime(2019, 8, 10).date()),
                'source_display_name': 'Featured Article 2',
                'is_starred': False,
                'url': featured_article_2.url,
            },
            {
                'id': featured_article_3.id,
                'title': featured_article_3.title,
                'published_date': str(datetime(2018, 8, 10).date()),
                'source_display_name': 'Featured Article 3',
                'is_starred': False,
                'url': featured_article_3.url,
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    @patch('departments.views.DEPARTMENTS_LIMIT', 3)
    def test_officers_with_maximum_starred_news_articles(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        department = DepartmentFactory()

        EventFactory(
            department=department,
            officer=officer,
        )

        starred_article_source_1 = NewsArticleSourceFactory(source_display_name='Starred Article 1')
        starred_article_source_2 = NewsArticleSourceFactory(source_display_name='Starred Article 2')
        starred_article_source_3 = NewsArticleSourceFactory(source_display_name='Starred Article 3')

        starred_article_1 = NewsArticleFactory(
            source=starred_article_source_1,
            published_date=datetime(2019, 1, 1),
        )
        starred_article_2 = NewsArticleFactory(
            source=starred_article_source_2,
            published_date=datetime(2018, 7, 1),
        )
        starred_article_3 = NewsArticleFactory(
            source=starred_article_source_3,
            published_date=datetime(2018, 1, 1),
        )

        department.starred_news_articles.add(starred_article_1, starred_article_2, starred_article_3)
        department.save()

        featured_article_source = NewsArticleSourceFactory(source_display_name='Featured Article')
        featured_article = NewsArticleFactory(
            source=featured_article_source,
        )
        matched_sentence = MatchedSentenceFactory(article=featured_article)
        matched_sentence.officers.add(officer)
        matched_sentence.save()

        response = self.auth_client.get(
            reverse('api:departments-news-articles', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': starred_article_1.id,
                'title': starred_article_1.title,
                'published_date': str(datetime(2019, 1, 1).date()),
                'source_display_name': 'Starred Article 1',
                'is_starred': True,
                'url': starred_article_1.url,
            },
            {
                'id': starred_article_2.id,
                'title': starred_article_2.title,
                'published_date': str(datetime(2018, 7, 1).date()),
                'source_display_name': 'Starred Article 2',
                'is_starred': True,
                'url': starred_article_2.url,
            },
            {
                'id': starred_article_3.id,
                'title': starred_article_3.title,
                'published_date': str(datetime(2018, 1, 1).date()),
                'source_display_name': 'Starred Article 3',
                'is_starred': True,
                'url': starred_article_3.url,
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    def test_featured_documents_not_found(self):
        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_featured_documents_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-documents', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_featured_documents_success(self):
        current_date = datetime.now(pytz.utc)

        department = DepartmentFactory()

        starred_document = DocumentFactory(incident_date=datetime(2017, 8, 10))
        department.starred_documents.add(starred_document)
        starred_document.departments.add(department)

        featured_document_1 = DocumentFactory(incident_date=current_date)
        featured_document_1.departments.add(department)

        featured_document_2 = DocumentFactory(incident_date=datetime(2017, 11, 10))
        featured_document_2.departments.add(department)

        featured_document_3 = DocumentFactory(incident_date=datetime(2017, 8, 10))
        featured_document_3.departments.add(department)

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': starred_document.id,
                'title': starred_document.title,
                'url': starred_document.url,
                'incident_date': str(datetime(2017, 8, 10).date()),
                'preview_image_url': starred_document.preview_image_url,
                'pages_count': starred_document.pages_count,
                'is_starred': True,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
            {
                'id': featured_document_1.id,
                'title': featured_document_1.title,
                'url': featured_document_1.url,
                'incident_date': str(current_date.date()),
                'preview_image_url': featured_document_1.preview_image_url,
                'pages_count': featured_document_1.pages_count,
                'is_starred': False,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
            {
                'id': featured_document_2.id,
                'title': featured_document_2.title,
                'url': featured_document_2.url,
                'incident_date': str(datetime(2017, 11, 10).date()),
                'preview_image_url': featured_document_2.preview_image_url,
                'pages_count': featured_document_2.pages_count,
                'is_starred': False,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
            {
                'id': featured_document_3.id,
                'title': featured_document_3.title,
                'url': featured_document_3.url,
                'incident_date': str(datetime(2017, 8, 10).date()),
                'preview_image_url': featured_document_3.preview_image_url,
                'pages_count': featured_document_3.pages_count,
                'is_starred': False,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    @patch('departments.views.DEPARTMENTS_LIMIT', 3)
    def test_officers_with_maximum_starred_documents(self):
        department = DepartmentFactory()

        starred_documents = DocumentFactory.create_batch(3)
        for document in starred_documents:
            department.starred_documents.add(document)
            document.departments.add(department)

        featured_document = DocumentFactory()
        featured_document.departments.add(department)

        response = self.auth_client.get(
            reverse('api:departments-documents', kwargs={'pk': department.slug})
        )

        expected_result = [
            {
                'id': starred_documents[0].id,
                'title': starred_documents[0].title,
                'url': starred_documents[0].url,
                'incident_date': str(starred_documents[0].incident_date),
                'preview_image_url': starred_documents[0].preview_image_url,
                'pages_count': starred_documents[0].pages_count,
                'is_starred': True,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
            {
                'id': starred_documents[1].id,
                'title': starred_documents[1].title,
                'url': starred_documents[1].url,
                'incident_date': str(starred_documents[1].incident_date),
                'preview_image_url': starred_documents[1].preview_image_url,
                'pages_count': starred_documents[1].pages_count,
                'is_starred': True,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
            {
                'id': starred_documents[2].id,
                'title': starred_documents[2].title,
                'url': starred_documents[2].url,
                'incident_date': str(starred_documents[2].incident_date),
                'preview_image_url': starred_documents[2].preview_image_url,
                'pages_count': starred_documents[2].pages_count,
                'is_starred': True,
                'departments': [
                    {
                        'id': department.slug,
                        'name': department.name,
                    }
                ]
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    def test_search_without_query(self):
        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-search', kwargs={'pk': 'slug'})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_officers_with_empty_results(self):
        officer_1 = OfficerFactory(first_name='Ray', last_name='Miley')
        officer_2 = OfficerFactory(first_name='Grayven', last_name='Miley')
        person_1 = PersonFactory(canonical_officer=officer_2, all_complaints_count=150)
        person_1.officers.add(officer_1)
        person_1.officers.add(officer_2)
        person_1.save()

        department = DepartmentFactory()

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="100",
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="250",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="150",
            year=2019,
            month=4,
            day=5,
        )

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'Sean',
                'kind': 'officers',
            }
        )

        expected_results = []

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_officers_success(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory(first_name='Ray', last_name='Miley', department=department)
        officer_2 = OfficerFactory(first_name='Grayven', last_name='Miley', department=department)
        person_1 = PersonFactory(canonical_officer=officer_2, all_complaints_count=150)
        person_1.officers.add(officer_1)
        person_1.officers.add(officer_2)
        person_1.save()

        officer_3 = OfficerFactory(first_name='Tom', last_name='Ray', department=department)
        person_2 = PersonFactory(canonical_officer=officer_3, all_complaints_count=100)
        person_2.officers.add(officer_3)
        person_2.save()

        officer_4 = OfficerFactory(first_name='Sean', last_name='Ray1', department=department)
        person_3 = PersonFactory(canonical_officer=officer_4, all_complaints_count=110)
        person_3.officers.add(officer_4)
        person_3.save()

        officer_5 = OfficerFactory(first_name='Sean', last_name='Dang', department=department)
        person_4 = PersonFactory(canonical_officer=officer_5, all_complaints_count=110)
        person_4.officers.add(officer_5)
        person_4.save()

        officer_6 = OfficerFactory(first_name='Jay', last_name='Dang')
        person_5 = PersonFactory(canonical_officer=officer_6)
        person_5.officers.add(officer_6)
        person_5.save()

        use_of_force_1 = UseOfForceFactory()
        use_of_force_2 = UseOfForceFactory()
        use_of_force_3 = UseOfForceFactory()

        UseOfForceOfficerFactory(officer=officer_5, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(officer=officer_3, use_of_force=use_of_force_2)
        UseOfForceOfficerFactory(officer=officer_4, use_of_force=use_of_force_3)

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="100",
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="250",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="150",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_2 = EventFactory(
            department=department,
            officer=officer_3,
            kind=UOF_RECEIVE,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        uof_incident_event_2 = EventFactory(
            department=department,
            officer=officer_4,
            kind=UOF_OCCUR,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            badge_no="123",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_1 = EventFactory(
            department=department,
            officer=officer_5,
            kind=UOF_RECEIVE,
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_4,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            rank_desc="sergeant",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department,
            officer=officer_4,
            rank_desc="recruit",
            year=2020,
            month=4,
            day=5,
        )

        use_of_force_1.events.add(uof_receive_event_1)
        use_of_force_2.events.add(uof_receive_event_2)
        use_of_force_3.events.add(uof_incident_event_2)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'Ray',
                'kind': 'officers',
            }
        )

        expected_results = [
            {
                'id': officer_3.id,
                'name': officer_3.name,
                'is_starred': False,
                'use_of_forces_count': 1,
                'badges': ["123", "200"],
                'complaints_count': officer_3.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'sergeant',
            },
            {
                'id': officer_4.id,
                'name': officer_4.name,
                'is_starred': False,
                'use_of_forces_count': 1,
                'badges': ["200"],
                'complaints_count': officer_4.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'recruit',
            },
            {
                'id': officer_2.id,
                'name': officer_2.name,
                'is_starred': False,
                'use_of_forces_count': 0,
                'badges': ["150", "100", "250"],
                'complaints_count': officer_2.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'senior',
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_officers_with_limit_and_offset(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory(first_name='Ray', last_name='Miley', department=department)
        officer_2 = OfficerFactory(first_name='Grayven', last_name='Miley', department=department)
        person_1 = PersonFactory(canonical_officer=officer_2, all_complaints_count=150)
        person_1.officers.add(officer_1)
        person_1.officers.add(officer_2)
        person_1.save()

        officer_3 = OfficerFactory(first_name='Tom', last_name='Ray', department=department)
        person_2 = PersonFactory(canonical_officer=officer_3, all_complaints_count=100)
        person_2.officers.add(officer_3)
        person_2.save()

        officer_4 = OfficerFactory(first_name='Sean', last_name='Ray1', department=department)
        person_3 = PersonFactory(canonical_officer=officer_4, all_complaints_count=110)
        person_3.officers.add(officer_4)
        person_3.save()

        officer_5 = OfficerFactory(first_name='Sean', last_name='Dang', department=department)
        person_4 = PersonFactory(canonical_officer=officer_5, all_complaints_count=110)
        person_4.officers.add(officer_5)
        person_4.save()

        officer_6 = OfficerFactory(first_name='Jay', last_name='Dang')
        person_5 = PersonFactory(canonical_officer=officer_6)
        person_5.officers.add(officer_6)
        person_5.save()

        use_of_force_1 = UseOfForceFactory()
        use_of_force_2 = UseOfForceFactory()
        use_of_force_3 = UseOfForceFactory()

        UseOfForceOfficerFactory(officer=officer_5, use_of_force=use_of_force_1)
        UseOfForceOfficerFactory(officer=officer_3, use_of_force=use_of_force_2)
        UseOfForceOfficerFactory(officer=officer_4, use_of_force=use_of_force_3)

        EventFactory(
            department=department,
            officer=officer_1,
            badge_no="100",
            year=2018,
            month=8,
            day=3,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="250",
            year=2018,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_2,
            badge_no="150",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_2 = EventFactory(
            department=department,
            officer=officer_3,
            kind=UOF_RECEIVE,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        uof_incident_event_2 = EventFactory(
            department=department,
            officer=officer_4,
            kind=UOF_OCCUR,
            badge_no="200",
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_3,
            badge_no="123",
            year=2019,
            month=4,
            day=5,
        )

        uof_receive_event_1 = EventFactory(
            department=department,
            officer=officer_5,
            kind=UOF_RECEIVE,
            year=2018,
            month=8,
            day=20,
        )

        EventFactory(
            department=department,
            officer=officer_4,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=department,
            officer=officer_4,
            rank_desc="recruit",
            year=2020,
            month=4,
            day=5,
        )

        use_of_force_1.events.add(uof_receive_event_1)
        use_of_force_2.events.add(uof_receive_event_2)
        use_of_force_3.events.add(uof_incident_event_2)

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'Ray',
                'kind': 'officers',
                'limit': 1,
                'offset': 1,
            }
        )

        expected_results = [
            {
                'id': officer_4.id,
                'name': officer_4.name,
                'is_starred': False,
                'use_of_forces_count': 1,
                'badges': ["200"],
                'complaints_count': officer_4.person.all_complaints_count,
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'recruit',
            }
        ]

        expected_previous = f'http://testserver/api/departments/{department.slug}/search/?kind=officers&limit=1&q=Ray'
        expected_next = f'http://testserver/api/departments/{department.slug}/search/?kind=officers&limit=1&offset=2&q=Ray'

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] == expected_previous
        assert response.data['next'] == expected_next
        assert response.data['results'] == expected_results

    def test_search_news_articles_with_empty_results(self):
        officer = OfficerFactory()
        department = DepartmentFactory()
        source = NewsArticleSourceFactory(source_display_name='Source')

        NewsArticleFactory(
            title='Document title keyword',
            content='Text content',
            source=source,
            author='dummy'
        )

        news_article_1 = NewsArticleFactory(
            title='News article keyword1',
            content='Text content 1',
            source=source)
        news_article_2 = NewsArticleFactory(
            title='News article 2',
            content='Text content keyword 2',
            source=source,
        )
        news_article_3 = NewsArticleFactory(
            title='Document title',
            content='Text content',
            source=source,
            author='dummy'
        )

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)
        matched_sentence_3.officers.add(officer)

        EventFactory(
            department=department,
            officer=officer,
        )

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'Sean',
                'kind': 'news_articles',
            }
        )

        expected_results = []

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_news_articles_success(self):
        department = DepartmentFactory()
        officer = OfficerFactory(department=department)
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        source = NewsArticleSourceFactory(source_display_name='Source')

        NewsArticleFactory(
            title='Document title keyword',
            content='Text content',
            source=source,
            author='dummy'
        )

        news_article_1 = NewsArticleFactory(
            title='News article skeyword1',
            content='Text content 1',
            source=source,
        )
        news_article_2 = NewsArticleFactory(
            title='Document title',
            content='Text content',
            source=source,
            author='dummy'
        )

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)

        EventFactory(
            department=department,
            officer=officer,
        )

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'keyword',
                'kind': 'news_articles',
            }
        )

        expected_results = [
            {
                'id': news_article_1.id,
                'source_name': 'Source',
                'title': news_article_1.title,
                'url': news_article_1.url,
                'date': str(news_article_1.published_date),
                'author': news_article_1.author,
                'content': news_article_1.content,
                'content_highlight': None,
                'author_highlight': None
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['previous'] is None
        assert response.data['next'] is None
        assert response.data['results'] == expected_results

    def test_search_news_articles_with_limit_and_offset(self):
        department = DepartmentFactory()
        officer = OfficerFactory(department=department)
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        source = NewsArticleSourceFactory(source_display_name='Source')

        NewsArticleFactory(
            title='Document title keyword',
            content='Text content',
            source=source,
            author='dummy'
        )

        news_article_1 = NewsArticleFactory(
            title='News article keyword',
            content='Text content',
            source=source,
        )
        news_article_2 = NewsArticleFactory(
            title='News article 2',
            content='Text content keyword 2',
            source=source,
        )
        news_article_3 = NewsArticleFactory(
            title='Document title',
            content='Text content',
            source=source,
            author='dummy'
        )
        news_article_4 = NewsArticleFactory(
            title='Documented title keyword',
            content='Text content',
            source=source,
            author='keyword'
        )

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_3 = MatchedSentenceFactory(article=news_article_3)
        matched_sentence_4 = MatchedSentenceFactory(article=news_article_4)
        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)
        matched_sentence_3.officers.add(officer)
        matched_sentence_4.officers.add(officer)

        EventFactory(
            department=department,
            officer=officer,
        )

        rebuild_search_index()

        response = self.auth_client.get(
            reverse('api:departments-search', kwargs={'pk': department.slug}),
            {
                'q': 'keyword',
                'kind': 'news_articles',
                'limit': '1',
                'offset': '1',
            }
        )

        expected_previous = f'http://testserver/api/departments/{department.slug}/search/?kind=news_articles&limit=1&q=keyword'
        expected_next = f'http://testserver/api/departments/{department.slug}/search/?kind=news_articles&limit=1&offset=2&q=keyword'

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        assert response.data['previous'] == expected_previous
        assert response.data['next'] == expected_next

    def test_migratory_unauthorized(self):
        response = self.client.get(
            reverse('api:departments-migratory')
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_migratory_list_success(self):
        start_department = DepartmentFactory()
        end_department = DepartmentFactory()
        DepartmentFactory()

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2019,
            month=4,
            day=5,
        )

        event = EventFactory(
            department=end_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2019,
            month=6,
            day=5,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2019,
            month=5,
            day=8,
        )

        start_department_location = tuple(float(coordinate) for coordinate in findall(r'[-+]?(?:\d*\.\d+|\d+)', start_department.location))
        end_department_location = tuple(float(coordinate) for coordinate in findall(r'[-+]?(?:\d*\.\d+|\d+)', end_department.location))

        expected_result = {
            'nodes': {
                start_department.slug: {
                    'name': start_department.name,
                    'location': start_department_location,
                },
                end_department.slug: {
                    'name': end_department.name,
                    'location': end_department_location,
                },
            },
            'graphs': [
                {
                    'start_node': start_department.slug,
                    'end_node': end_department.slug,
                    'start_location': start_department_location,
                    'end_location': end_department_location,
                    'year': 2019,
                    'date': parse_date(event.year, event.month, event.day),
                    'officer_name': officer_1.name,
                    'officer_id': officer_1.id,
                },
            ]
        }

        response = self.auth_client.get(
            reverse('api:departments-migratory')
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    def test_migratory_list_empty(self):
        start_department = DepartmentFactory()
        end_department = DepartmentFactory()

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2018,
            month=2,
            day=3,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=3,
            day=3,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2019,
            month=4,
            day=5,
        )

        EventFactory(
            department=end_department,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=None,
            month=None,
            day=None,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2019,
            month=5,
            day=8,
        )

        expected_result = {
            'nodes': {},
            'graphs': []
        }

        response = self.auth_client.get(
            reverse('api:departments-migratory')
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result

    def test_migratory_list_with_no_department_location(self):
        start_department = DepartmentFactory()
        end_department1 = DepartmentFactory()
        end_department2 = DepartmentFactory(location=None)
        DepartmentFactory()

        officer_1 = OfficerFactory()
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory()
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=OFFICER_LEFT,
            year=2019,
            month=4,
            day=5,
        )

        event = EventFactory(
            department=end_department1,
            officer=officer_1,
            kind=OFFICER_HIRE,
            year=2019,
            month=6,
            day=5,
        )

        EventFactory(
            department=start_department,
            officer=officer_2,
            kind=OFFICER_LEFT,
            year=2019,
            month=5,
            day=5,
        )

        EventFactory(
            department=end_department2,
            officer=officer_2,
            kind=OFFICER_HIRE,
            year=2020,
            month=6,
            day=5,
        )

        EventFactory(
            department=start_department,
            officer=officer_1,
            kind=UOF_OCCUR,
            year=2019,
            month=5,
            day=8,
        )

        EventFactory(
            department=start_department,
            officer=officer_2,
            kind=UOF_RECEIVE,
        )

        start_department_location = tuple(float(coordinate) for coordinate in findall(r'[-+]?(?:\d*\.\d+|\d+)', start_department.location))
        end_department_location = tuple(float(coordinate) for coordinate in findall(r'[-+]?(?:\d*\.\d+|\d+)', end_department1.location))

        expected_result = {
            'nodes': {
                start_department.slug: {
                    'name': start_department.name,
                    'location': start_department_location,
                },
                end_department1.slug: {
                    'name': end_department1.name,
                    'location': end_department_location,
                },
            },
            'graphs': [
                {
                    'start_node': start_department.slug,
                    'end_node': end_department1.slug,
                    'start_location': start_department_location,
                    'end_location': end_department_location,
                    'year': 2019,
                    'date': parse_date(event.year, event.month, event.day),
                    'officer_name': officer_1.name,
                    'officer_id': officer_1.id,
                },
            ]
        }

        response = self.auth_client.get(
            reverse('api:departments-migratory')
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_result
