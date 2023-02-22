from datetime import date

from django.test import TestCase

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from officers.factories import EventFactory, OfficerFactory
from search.queries.documents_search_query import DocumentsSearchQuery
from utils.search_index import rebuild_search_index


class DocumentsSearchQueryTestCase(TestCase):
    def test_query(self):
        DocumentFactory(title="Document title", text_content="Text content")
        document_1 = DocumentFactory(
            title="Document keyword1", text_content="Text content 1"
        )
        document_2 = DocumentFactory(
            title="Document 2", text_content="Text content keyword 2"
        )

        rebuild_search_index()

        result = DocumentsSearchQuery("keyword").search()
        document_ids = {item["id"] for item in result}

        assert document_ids == {document_1.id, document_2.id}

    def test_query_with_matched_by_officer_names(self):
        document_1 = DocumentFactory(title="Document 1", text_content="Text content 1")
        document_2 = DocumentFactory(title="Document 2", text_content="Text content 2")
        document_3 = DocumentFactory(title="Document 3", text_content="Text content 3")
        document_4 = DocumentFactory(title="Document 4", text_content="Text content 4")

        officer_1 = OfficerFactory(first_name="David", last_name="Jonesworth")
        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis")
        officer_3 = OfficerFactory(first_name="Kenneth", last_name="Anderson")

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)
        document_4.officers.add(officer_3)

        rebuild_search_index()

        result = DocumentsSearchQuery("Davi").search()
        document_ids = {item["id"] for item in result}

        assert document_ids == {document_1.id, document_2.id, document_3.id}

    def test_query_with_matched_by_officer_badges(self):
        document_1 = DocumentFactory(title="Document 1", text_content="Text content 1")
        document_2 = DocumentFactory(title="Document 2", text_content="Text content 2")
        document_3 = DocumentFactory(title="Document 3", text_content="Text content 3")

        officer_1 = OfficerFactory(first_name="David", last_name="Jonesworth")
        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis")

        EventFactory(officer=officer_1, badge_no="12435")
        EventFactory(officer=officer_2, badge_no="45812")

        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)
        document_3.officers.add(officer_2)

        rebuild_search_index()

        result = DocumentsSearchQuery("45812").search()
        document_ids = {item["id"] for item in result}

        assert document_ids == {document_2.id, document_3.id}

    def test_query_with_matched_by_department_names(self):
        document_1 = DocumentFactory(
            title="Document 1",
            text_content="Text content 1",
            incident_date=date(2019, 10, 12),
        )
        document_2 = DocumentFactory(
            title="Document 2",
            text_content="Text content 2",
            incident_date=date(2020, 4, 7),
        )
        document_3 = DocumentFactory(
            title="Document 3",
            text_content="Text content 3",
            incident_date=date(2017, 1, 2),
        )
        document_4 = DocumentFactory(title="Document 4", text_content="Text content 4")
        document_5 = DocumentFactory(title="Document 5", text_content="Text content 5")

        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        for document in [document_1, document_2, document_5]:
            document.departments.add(department_1)
        for document in [document_3, document_4]:
            document.departments.add(department_2)

        rebuild_search_index()

        result = DocumentsSearchQuery("Orlean").search()
        document_ids = {item["id"] for item in result}

        assert document_ids == {document_1.id, document_2.id, document_5.id}
