from datetime import date

from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory
from officers.constants import (
    JOINED_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND
)
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
)
from officers.constants import COMPLAINT_RECEIVE, ALLEGATION_CREATE


class OfficersViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')
        department = DepartmentFactory()

        EventFactory(
            officer=officer_1,
            department=department,
            badge_no='67893',
            year=2017,
            month=None,
            day=None,
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
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer_1,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
        )

        response = self.auth_client.get(reverse('api:officers-list'))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == [
            {
                'id': officer_2.id,
                'name': 'Anthony Davis',
                'badges': [],
                'department': None,
            },
            {
                'id': officer_1.id,
                'name': 'David Jonesworth',
                'badges': ['12435', '67893', '5432'],
                'department': {
                    'id': department.id,
                    'name': department.name,
                },
            }]

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:officers-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_success(self):
        officer = OfficerFactory(
            first_name='David',
            last_name='Jonesworth',
            birth_year=1962,
            race='white',
            gender='male',
        )
        department = DepartmentFactory()
        EventFactory(
            officer=officer,
            department=department,
            badge_no='12435',
            annual_salary='57K',
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='67893',
            annual_salary='20K',
            year=2017,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            department=department,
            badge_no='5432',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            badge_no=None,
            year=2015,
            month=7,
            day=20,
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
        )
        EventFactory(
            officer=officer,
            kind=ALLEGATION_CREATE,
            badge_no=None,
            year=2020,
            month=5,
            day=4,
        )

        expected_result = {
            'id': officer.id,
            'name': 'David Jonesworth',
            'badges': ['12435', '67893', '5432'],
            'birth_year': 1962,
            'race': 'white',
            'gender': 'male',
            'department': {
                'id': department.id,
                'name': department.name,
            },
            'annual_salary': '57K',
            'documents_count': 3,
            'complaints_count': 2,
            'data_period': ['2015-2020'],
            'complaints_data_period': ['2019-2020'],
            'documents_data_period': ['2016-2018'],
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

    def test_documents_success(self):
        department = DepartmentFactory()
        officer = OfficerFactory()

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))

        for document in [document_1, document_2, document_3]:
            document.officers.add(officer)

        document_1.departments.add(department)

        expected_results = [{
            'id': document_1.id,
            'document_type': document_1.document_type,
            'title': document_1.title,
            'url': document_1.url,
            'incident_date': str(document_1.incident_date),
            'preview_image_url': document_1.preview_image_url,
            'pages_count': document_1.pages_count,
            'text_content': document_1.text_content,
            'departments': [
                {
                    'id': department.id,
                    'name': department.name
                }
            ]
        }, {
            'id': document_3.id,
            'document_type': document_3.document_type,
            'title': document_3.title,
            'url': document_3.url,
            'incident_date': str(document_3.incident_date),
            'preview_image_url': document_3.preview_image_url,
            'pages_count': document_3.pages_count,
            'text_content': document_3.text_content,
            'departments': []
        }, {
            'id': document_2.id,
            'document_type': document_2.document_type,
            'title': document_2.title,
            'url': document_2.url,
            'incident_date': str(document_2.incident_date),
            'preview_image_url': document_2.preview_image_url,
            'pages_count': document_2.pages_count,
            'text_content': document_2.text_content,
            'departments': []
        }]

        response = self.auth_client.get(
            reverse('api:officers-documents', kwargs={'pk': officer.id})
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_results

    def test_documents_not_found(self):
        response = self.auth_client.get(
            reverse('api:officers-documents', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_documents_unauthorized(self):
        response = self.client.get(
            reverse('api:officers-documents', kwargs={'pk': 1})
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_timeline_success(self):
        officer = OfficerFactory()
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
            annual_salary='57k',
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

        document_1 = DocumentFactory(incident_date=date(2018, 6, 5))
        document_2 = DocumentFactory(incident_date=date(2021, 2, 1))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_1.departments.add(department_1)

        expected_result = [
            {
                'id': complaint_2.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': None,
                'year': None,
                'rule_code': complaint_2.rule_code,
                'rule_violation': complaint_2.rule_violation,
                'paragraph_violation': complaint_2.paragraph_violation,
                'disposition': complaint_2.disposition,
                'action': complaint_2.action,
                'tracking_number': complaint_2.tracking_number,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'senior police office',
                'date': str(date(2017, 7, 13)),
                'year': 2017,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2018, 4, 8)),
                'year': 2018,
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
                        'id': department_1.id,
                        'name': department_1.name,
                    },
                ],
            },
            {
                'id': complaint_1.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': str(date(2019, 5, 4)),
                'year': 2019,
                'rule_code': complaint_1.rule_code,
                'rule_violation': complaint_1.rule_violation,
                'paragraph_violation': complaint_1.paragraph_violation,
                'disposition': complaint_1.disposition,
                'action': complaint_1.action,
                'tracking_number': complaint_1.tracking_number,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '57k',
                'date': str(date(2019, 12, 1)),
                'year': 2019,
            },
            {
                'kind': LEFT_TIMELINE_KIND,
                'date': str(date(2020, 4, 8)),
                'year': 2020,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2020, 5, 9)),
                'year': 2020,
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
        ]

        response = self.auth_client.get(
            reverse('api:officers-timeline', kwargs={'pk': officer.id})
        )

        data = sorted(
            response.data,
            key=lambda item: str(item['date']) if item['date'] else ''
        )

        assert response.status_code == status.HTTP_200_OK
        assert data == expected_result

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
