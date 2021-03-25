import pytz
from operator import itemgetter
from datetime import datetime, date

from django.test import TestCase

from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from search.queries.search_all_query import SearchAllQuery
from utils.search_index import rebuild_search_index


class OfficersSearchQueryTestCase(TestCase):
    def test_query(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans keyword PD')
        department_2 = DepartmentFactory(name='Orleans keywo PD')

        OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_1 = OfficerFactory(first_name='David keyword', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis keywords')

        OfficerHistoryFactory(
            officer=officer_1,
            department=department_1,
            badge_no='12435',
            start_date=datetime(2020, 5, 4, tzinfo=pytz.utc),
            end_date=datetime(2021, 5, 4, tzinfo=pytz.utc),
        )

        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 6)
        )
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keywo')
        document_1.officers.add(officer_1)

        rebuild_search_index()

        expected_result = {
            'DEPARTMENTS': [
                {
                    'id': department_1.id,
                    'name': department_1.name,
                    'city': department_1.city,
                    'parish': department_1.parish,
                    'location_map_url': department_1.location_map_url,
                },
                {
                    'id': department_2.id,
                    'name': department_2.name,
                    'city': department_2.city,
                    'parish': department_2.parish,
                    'location_map_url': department_2.location_map_url,
                },
            ],
            'OFFICERS': [
                {
                    'id': officer_1.id,
                    'name': officer_1.name,
                    'badges': ['12435'],
                    'department': {
                        'id': department_1.id,
                        'name': department_1.name,
                    },
                },
                {
                    'id': officer_2.id,
                    'name': officer_2.name,
                    'badges': [],
                    'department': None,
                },
            ],
            'DOCUMENTS': [
                {
                    'id': document_1.id,
                    'document_type': document_1.document_type,
                    'title': document_1.title,
                    'url': document_1.url,
                    'incident_date': str(document_1.incident_date),
                    'preview_image_url': document_1.preview_image_url,
                    'pages_count': document_1.pages_count,
                    'text_content': document_1.text_content,
                    'text_content_highlight': None,
                    'departments': [
                        {
                            'id': department_1.id,
                            'name': department_1.name,
                        },
                    ],
                },
                {
                    'id': document_2.id,
                    'document_type': document_2.document_type,
                    'title': document_2.title,
                    'url': document_2.url,
                    'incident_date': str(document_2.incident_date),
                    'preview_image_url': document_2.preview_image_url,
                    'pages_count': document_2.pages_count,
                    'text_content': document_2.text_content,
                    'text_content_highlight': 'Text content <em>keywo</em>',
                    'departments': [],
                },
            ],
        }

        result = SearchAllQuery().search('keywo')

        for search_key, items in result.items():
            result[search_key] = sorted(items, key=itemgetter('id'))

        assert result == expected_result
