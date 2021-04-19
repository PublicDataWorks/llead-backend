from datetime import date
from operator import itemgetter

from django.urls import reverse

from rest_framework import status

from test_utils.auth_api_test_case import AuthAPITestCase
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory


class HistoricalDataViewSetTestCase(AuthAPITestCase):
    def test_recent_items(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no='12435',
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        response = self.auth_client.get(
            reverse('api:historical-data-recent-items'),
            {
                'department_ids[]': [department_1.id, department_2.id],
                'officer_ids[]': [officer.id],
                'document_ids[]': [document.id],
            }
        )

        expected_data = {
            'department': [
                {
                    'id': department_1.id,
                    'name': department_1.name,
                    'city': department_1.city,
                    'parish': department_1.parish,
                    'location_map_url': department_1.location_map_url,
                }, {
                    'id': department_2.id,
                    'name': department_2.name,
                    'city': department_2.city,
                    'parish': department_2.parish,
                    'location_map_url': department_2.location_map_url,
                }
            ],
            'officer': [
                {
                    'id': officer.id,
                    'name': 'David Jonesworth',
                    'badges': ['12435'],
                    'department': {
                        'id': department_2.id,
                        'name': department_2.name,
                    }
                }
            ],
            'document': [
                {
                    'id': document.id,
                    'document_type': document.document_type,
                    'title': document.title,
                    'url': document.url,
                    'preview_image_url': document.preview_image_url,
                    'incident_date': str(document.incident_date),
                    'pages_count': document.pages_count,
                    'departments': [
                        {
                            'id': department_1.id,
                            'name': department_1.name,
                        }
                    ],
                },
            ]
        }

        result = response.data
        result['department'] = sorted(result['department'], key=itemgetter('id'))

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
