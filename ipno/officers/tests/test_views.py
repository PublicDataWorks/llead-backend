from datetime import date

from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class OfficersViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        department = DepartmentFactory()
        OfficerHistoryFactory(
            officer=officer_1,
            badge_no='612',
            start_date=date(2017, 1, 5)
        )
        OfficerHistoryFactory(
            officer=officer_1,
            department=department,
            badge_no='12435',
            start_date=date(2020, 5, 4)
        )
        OfficerHistoryFactory(
            officer=officer_1,
            badge_no=None,
            start_date=date(2015, 7, 20)
        )

        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')

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
                'badges': ['12435', '612'],
                'department': {
                    'id': department.id,
                    'name': department.name,
                },
            }]

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:officers-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
