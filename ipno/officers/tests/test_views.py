from datetime import date
from io import BytesIO as IO

from django.urls import reverse

from rest_framework import status

from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from unittest.mock import patch
import pandas as pd

from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, EventFactory
from use_of_forces.factories import UseOfForceFactory, UseOfForceOfficerFactory, UseOfForceCitizenFactory
from officers.constants import (
    COMPLAINT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    JOINED_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
    UOF_TIMELINE_KIND, NEWS_ARTICLE_TIMELINE_KIND,
)
from officers.constants import (
    OFFICER_DEPT,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    UOF_RECEIVE,
)
from officers.constants import COMPLAINT_RECEIVE, ALLEGATION_CREATE


class OfficersViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            department=department,
        )
        person_1 = PersonFactory(
            canonical_officer=officer_1,
            all_complaints_count=4,
         )
        person_1.officers.add(officer_1)
        officer_1.person = person_1
        officer_2 = OfficerFactory(
            first_name='Anthony',
            last_name='Davis',
            department=department,
        )
        person_2 = PersonFactory(
            canonical_officer=officer_2,
            all_complaints_count=7,
        )
        person_2.officers.add(officer_2)
        officer_2.person = person_2
        OfficerFactory()

        EventFactory(
            officer=officer_1,
            department=department,
            badge_no='67893',
            year=2017,
            month=11,
            day=4,
        )

        EventFactory(
            officer=officer_1,
            department=department,
            badge_no='12435',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department,
            badge_no='5432',
            year=2018,
            month=6,
            day=5,
        )
        EventFactory(
            officer=officer_1,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
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

        officer_1_complaints = ComplaintFactory.create_batch(2)
        officer_2_complaints = ComplaintFactory.create_batch(3)

        for complaint in officer_1_complaints:
            complaint.officers.add(officer_1)

        for complaint in officer_2_complaints:
            complaint.officers.add(officer_2)

        response = self.auth_client.get(reverse('api:officers-list'))

        expected_data = [
            {
                'id': officer_2.id,
                'name': 'Anthony Davis',
                'badges': [],
                'department':  {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'junior',
            },
            {
                'id': officer_1.id,
                'name': 'David Jonesworth',
                'badges': ['12435', '5432', '67893'],
                'department': {
                    'id': department.slug,
                    'name': department.name,
                },
                'latest_rank': 'senior',
            }]

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:officers-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self):
        department = DepartmentFactory()

        person = PersonFactory()
        related_officer = OfficerFactory()
        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            sex='male',
            person=person,
            department=department
        )
        person.officers.add(related_officer)
        person.canonical_officer = officer
        person.save()
        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            salary='57000',
            salary_freq='yearly',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            salary='20000',
            salary_freq='yearly',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='5432',
            year=2018,
            month=11,
            day=4,
        )
        EventFactory(
            officer=officer,
            badge_no='12435',
            year=2015,
            month=7,
            day=20,
            department=None,
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()

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
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        expected_result = {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435', '5432', '67893'],
            'birth_year': 1962,
            'race': 'white',
            'sex': 'male',
            'departments': [{
                'id': department.slug,
                'name': department.name,
            }],
            'latest_rank': 'senior',
            'salary': '57000.00',
            'salary_freq': 'yearly',
            'documents_count': 3,
            'complaints_count': 2,
        }

        response = self.auth_client.get(
            reverse('api:officers-detail', kwargs={'pk': officer.id})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result

    def test_retrieve_not_found(self):
        response = self.auth_client.get(
            reverse('api:officers-detail', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_unauthorized(self):
        response = self.client.get(
            reverse('api:officers-detail', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_timeline_success(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_PAY_EFFECTIVE,
            salary='57000',
            salary_freq='yearly',
            year=2019,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            department=department_2,
            kind=OFFICER_HIRE,
            year=2020,
            month=5,
            day=9,
        )
        EventFactory(
            officer=officer,
            department=department_2,
            kind=OFFICER_RANK,
            rank_desc='senior police office',
            rank_code=3,
            year=2017,
            month=7,
            day=13,
        )
        complaint_receive_event = EventFactory(
            officer=officer,
            department=department_1,
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        complaint_1.events.add(complaint_receive_event)

        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2017,
            month=7,
            day=14,
        )
        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2018,
            month=8,
            day=10,
        )

        document_1 = DocumentFactory(incident_date=date(2018, 6, 5))
        document_2 = DocumentFactory(incident_date=date(2021, 2, 1))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_1.departments.add(department_1)

        news_article_1 = NewsArticleFactory(published_date=date(2018, 6, 6))
        news_article_2 = NewsArticleFactory(published_date=date(2021, 2, 2))

        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)

        matched_sentence_1.officers.add(officer)
        matched_sentence_2.officers.add(officer)

        use_of_force = UseOfForceFactory()
        use_of_force_officer = UseOfForceOfficerFactory(officer=officer, use_of_force=use_of_force)
        use_of_force_citizen = UseOfForceCitizenFactory(use_of_force=use_of_force)
        EventFactory(
            kind=UOF_RECEIVE,
            year=2019,
            month=5,
            day=5,
            use_of_force=use_of_force,
        )

        expected_result = [
            {
                'id': complaint_2.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': None,
                'year': None,
                'disposition': complaint_2.disposition,
                'allegation': complaint_2.allegation,
                'allegation_desc': complaint_2.allegation_desc,
                'action': complaint_2.action,
                'tracking_id': complaint_2.tracking_id,
                'citizen_arrested': complaint_2.citizen_arrested,
                'traffic_stop': complaint_2.traffic_stop,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'senior police office',
                'rank_code': '3',
                'date': str(date(2017, 7, 13)),
                'year': 2017,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '193',
                'department_desc': 'Gang Investigation Division',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': str(date(2017, 7, 14)),
                'year': 2017,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2018, 4, 8)),
                'year': 2018,
                'department': department_1.name,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_1.incident_date),
                'year': document_1.incident_date.year,
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'preview_image_url': document_1.preview_image_url,
                'incident_date': str(document_1.incident_date),
                'pages_count': document_1.pages_count,
                'departments': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                    },
                ],
            },
            {
                'kind': NEWS_ARTICLE_TIMELINE_KIND,
                'date': str(news_article_1.published_date),
                'year': news_article_1.published_date.year,
                'id': news_article_1.id,
                'source_name': news_article_1.source.source_display_name,
                'title': news_article_1.title,
                'url': news_article_1.url,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': '193',
                'prev_department_desc': 'Gang Investigation Division',
                'date': str(date(2018, 8, 10)),
                'year': 2018,
            },
            {
                'id': complaint_1.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': str(date(2019, 5, 4)),
                'year': 2019,
                'disposition': complaint_1.disposition,
                'allegation': complaint_1.allegation,
                'allegation_desc': complaint_1.allegation_desc,
                'action': complaint_1.action,
                'tracking_id': complaint_1.tracking_id,
                'citizen_arrested': complaint_1.citizen_arrested,
                'traffic_stop': complaint_1.traffic_stop,
            },
            {
                'id': use_of_force_officer.id,
                'kind': UOF_TIMELINE_KIND,
                'date': str(date(2019, 5, 5)),
                'year': 2019,
                'use_of_force_description': use_of_force_officer.use_of_force_description,
                'use_of_force_reason': use_of_force.use_of_force_reason,
                'disposition': use_of_force.disposition,
                'service_type': use_of_force.service_type,
                'citizen_information': [str(use_of_force_citizen.citizen_age) + '-year-old '
                                        + use_of_force_citizen.citizen_race + ' ' + use_of_force_citizen.citizen_sex],
                'tracking_id': use_of_force.tracking_id,
                'citizen_arrested': [use_of_force_citizen.citizen_arrested],
                'citizen_injured': [use_of_force_citizen.citizen_injured],
                'citizen_hospitalized': [use_of_force_citizen.citizen_hospitalized],
                'officer_injured': use_of_force_officer.officer_injured,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'salary': '57000.00',
                'salary_freq': 'yearly',
                'date': str(date(2019, 12, 1)),
                'year': 2019,
            },
            {
                'kind': LEFT_TIMELINE_KIND,
                'date': str(date(2020, 4, 8)),
                'year': 2020,
                'department': department_1.name,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2020, 5, 9)),
                'year': 2020,
                'department': department_2.name,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_2.incident_date),
                'year': document_2.incident_date.year,
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'preview_image_url': document_2.preview_image_url,
                'incident_date': str(document_2.incident_date),
                'pages_count': document_2.pages_count,
                'departments': [],
            },
            {
                'kind': NEWS_ARTICLE_TIMELINE_KIND,
                'date': str(news_article_2.published_date),
                'year': news_article_2.published_date.year,
                'id': news_article_2.id,
                'source_name': news_article_2.source.source_display_name,
                'title': news_article_2.title,
                'url': news_article_2.url,
            },
        ]

        response = self.auth_client.get(
            reverse('api:officers-timeline', kwargs={'pk': officer.id})
        )

        timeline_data = sorted(
            response.data['timeline'],
            key=lambda item: str(item['date']) if item['date'] else ''
        )
        timeline_period_data = response.data['timeline_period']

        assert response.status_code == status.HTTP_200_OK
        assert timeline_data == expected_result
        assert timeline_period_data == ['2019']

    def test_timelime_not_found(self):
        response = self.auth_client.get(
            reverse('api:officers-timeline', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_timelime_unauthorized(self):
        response = self.client.get(
            reverse('api:officers-timeline', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_download_xlsx_not_found(self):
        response = self.auth_client.get(
            reverse('api:officers-download-xlsx', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_download_xlsx_unauthorized(self):
        response = self.client.get(
            reverse('api:officers-download-xlsx', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('officers.queries.officer_data_file_query.OfficerDatafileQuery.generate_sheets_file')
    def test_download_xlsx_success(self, generate_sheets_file_mock):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        data = pd.DataFrame([{'a': 1, 'b': 2}])

        excel_file = IO()
        xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')

        data.to_excel(xlwriter, 'Test', index=False)

        xlwriter.save()

        generate_sheets_file_mock.return_value = excel_file

        expected_content_disposition = f'attachment; filename=officer-{officer.id}.xlsx'

        response = self.auth_client.get(
            reverse('api:officers-download-xlsx', kwargs={'pk': officer.id})
        )
        content = response.content
        data_file = IO(content)
        xlsx_data = pd.read_excel(data_file, sheet_name='Test')

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Disposition'] == expected_content_disposition
        pd.testing.assert_frame_equal(xlsx_data, data)

    def test_retrieve_success_with_related_officer_departments_and_badges(self):
        department = DepartmentFactory()
        related_department = DepartmentFactory()

        person = PersonFactory()
        related_officer = OfficerFactory(department=related_department)
        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            sex='male',
            person=person,
            department=department,
        )
        person.officers.add(related_officer)
        person.canonical_officer = officer
        person.save()
        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            salary='57000',
            salary_freq='yearly',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            salary='20000',
            salary_freq='yearly',
            year=2017,
            month=11,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='5432',
            year=2018,
            month=6,
            day=5,
        )
        EventFactory(
            officer=officer,
            badge_no='12435',
            year=2015,
            month=7,
            day=20,
            department=None,
        )
        EventFactory(
            officer=related_officer,
            badge_no='13579',
            year=2021,
            month=7,
            day=20,
            department=related_department,
        )

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()

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
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        expected_result = {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['13579', '12435', '5432', '67893'],
            'birth_year': 1962,
            'race': 'white',
            'sex': 'male',
            'departments': [
                {
                    'id': department.slug,
                    'name': department.name,
                },
                {
                    'id': related_department.slug,
                    'name': related_department.name,
                }
            ],
            'latest_rank': 'senior',
            'salary': '57000.00',
            'salary_freq': 'yearly',
            'documents_count': 3,
            'complaints_count': 2,
        }

        response = self.auth_client.get(
            reverse('api:officers-detail', kwargs={'pk': officer.id})
        )
        assert response.status_code == status.HTTP_200_OK

        assert response.data == expected_result
