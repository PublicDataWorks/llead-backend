from datetime import date

from django.test import TestCase

from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, EventFactory
from departments.factories import DepartmentFactory
from departments.queries.documents_search_query import DocumentsSearchQuery
from utils.search_index import rebuild_search_index


class DocumentsSearchQueryTestCase(TestCase):
    def test_query(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1'
        )
        document_2 = DocumentFactory(
            title='Document 2',
            text_content='Text content keyword 2',
            incident_date=date(2019, 2, 3)
        )
        document_3 = DocumentFactory(
            title='Document 3',
            text_content='Text content 3',
            incident_date=date(2019, 2, 3)
        )
        document_4 = DocumentFactory(
            title='Document 4',
            text_content='Text content keyword 4',
            incident_date=date(2021, 5, 6)
        )

        for document in [document_1, document_2, document_3]:
            document.departments.add(department_1)
        document_4.departments.add(department_2)

        rebuild_search_index()

        result = DocumentsSearchQuery('keyword', department_id=department_1.id).search()
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_1.id, document_2.id}

    def test_query_with_matched_by_officer_names(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        document_1 = DocumentFactory(title='Document 1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content 2')
        document_3 = DocumentFactory(title='Document 3', text_content='Text content 3')
        document_4 = DocumentFactory(title='Document 4', text_content='Text content 4')
        document_5 = DocumentFactory(title='Document 5', text_content='Text content 5')

        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')
        officer_3 = OfficerFactory(first_name='Kenneth', last_name='Anderson')

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)
        document_4.officers.add(officer_3)
        document_5.officers.add(officer_2)

        for document in [document_1, document_2, document_3, document_4]:
            document.departments.add(department_1)
        document_5.departments.add(department_2)

        rebuild_search_index()

        result = DocumentsSearchQuery('Davi', department_id=department_1.id).search()
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_1.id, document_2.id, document_3.id}

    def test_query_with_matched_by_officer_badges(self):
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        document_1 = DocumentFactory(title='Document 1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content 2')
        document_3 = DocumentFactory(title='Document 3', text_content='Text content 3')
        document_4 = DocumentFactory(title='Document 4', text_content='Text content 4')

        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')

        EventFactory(officer=officer_1, badge_no='12435')
        EventFactory(officer=officer_2, badge_no='45812')

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)
        document_4.officers.add(officer_2)

        for document in [document_1, document_2, document_3]:
            document.departments.add(department_1)
        document_4.departments.add(department_2)

        rebuild_search_index()

        result = DocumentsSearchQuery('45812', department_id=department_1.id).search()
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_2.id, document_3.id}
