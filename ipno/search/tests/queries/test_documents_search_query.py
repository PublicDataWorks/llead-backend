from django.test import TestCase

from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory
from search.queries.documents_search_query import DocumentsSearchQuery
from utils.search_index import rebuild_search_index


class DocumentsSearchQueryTestCase(TestCase):
    def test_query(self):
        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(title='Document keyword1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keyword 2')

        rebuild_search_index()

        result = DocumentsSearchQuery().search('keyword')
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_1.id, document_2.id}

    def test_query_with_matched_by_officer_names(self):
        document_1 = DocumentFactory(title='Document 1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content 2')
        document_3 = DocumentFactory(title='Document 3', text_content='Text content 3')
        document_4 = DocumentFactory(title='Document 4', text_content='Text content 4')

        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')
        officer_3 = OfficerFactory(first_name='Kenneth', last_name='Anderson')

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)
        document_4.officers.add(officer_3)

        rebuild_search_index()

        result = DocumentsSearchQuery().search('Davi')
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_1.id, document_2.id, document_3.id}

    def test_query_with_matched_by_officer_badges(self):
        document_1 = DocumentFactory(title='Document 1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content 2')
        document_3 = DocumentFactory(title='Document 3', text_content='Text content 3')

        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')

        OfficerHistoryFactory(officer=officer_1, badge_no='12435')
        OfficerHistoryFactory(officer=officer_2, badge_no='45812')

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)

        rebuild_search_index()

        result = DocumentsSearchQuery().search('45812')
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_2.id, document_3.id}

    def test_query_with_matched_by_department_names(self):
        document_1 = DocumentFactory(title='Document 1', text_content='Text content 1')
        document_2 = DocumentFactory(title='Document 2', text_content='Text content 2')
        document_3 = DocumentFactory(title='Document 3', text_content='Text content 3')
        document_4 = DocumentFactory(title='Document 4', text_content='Text content 4')
        document_5 = DocumentFactory(title='Document 5', text_content='Text content 5')

        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')
        officer_3 = OfficerFactory(first_name='Kenneth', last_name='Anderson')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        OfficerHistoryFactory(officer=officer_1, department=department_1, badge_no='12435')
        OfficerHistoryFactory(officer=officer_2, department=department_1, badge_no='45812')
        OfficerHistoryFactory(officer=officer_3, department=department_2, badge_no='45812')

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)
        document_4.officers.add(officer_3)

        document_5.departments.add(department_1)

        rebuild_search_index()

        result = DocumentsSearchQuery().search('Orlean')
        document_ids = {item['id'] for item in result}

        assert document_ids == {document_1.id, document_2.id, document_3.id, document_5.id}
