from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory


class DepartmentsViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()

        department_1_officers = OfficerFactory.create_batch(2)
        department_2_officers = OfficerFactory.create_batch(5)

        for officer in department_1_officers:
            officer.departments.add(department_1)

        for officer in department_2_officers:
            officer.departments.add(department_2)

        response = self.auth_client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_200_OK

        assert response.data == [{
            'id': department_2.id,
            'name': department_2.name,
            'city': department_2.city,
            'parish': department_2.parish,
            'location_map_url': department_2.location_map_url,
        }, {
            'id': department_1.id,
            'name': department_1.name,
            'city': department_1.city,
            'parish': department_1.parish,
            'location_map_url': department_1.location_map_url,
        }, {
            'id': department_3.id,
            'name': department_3.name,
            'city': department_3.city,
            'parish': department_3.parish,
            'location_map_url': department_3.location_map_url,
        }]

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:departments-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
