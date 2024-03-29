from datetime import date
from operator import itemgetter
from unittest.mock import Mock

from django.test import TestCase

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.constants import OFFICER_HIRE, OFFICER_LEFT
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from search.queries.search_all_query import SearchAllQuery
from utils.search_index import rebuild_search_index


class OfficersSearchQueryTestCase(TestCase):
    def test_query(self):
        request = Mock(
            query_params={
                "limit": 2,
                "offset": 0,
            }
        )
        DepartmentFactory(agency_name="Baton Rouge PD")
        department_1 = DepartmentFactory(agency_name="New Orleans keyword PD")
        department_2 = DepartmentFactory(agency_name="Orleans keywo PD")

        OfficerFactory(first_name="Kenneth", last_name="Anderson")
        officer_1 = OfficerFactory(
            first_name="David keyword", last_name="Jonesworth", department=department_1
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis keywords")
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_HIRE,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            department=department_1,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        DocumentFactory(title="Document title", text_content="Text content")
        document_1 = DocumentFactory(
            title="Document keyword1",
            text_content="Text content 1",
            incident_date=date(2020, 5, 6),
        )
        document_2 = DocumentFactory(
            title="Document 2", text_content="Text content keywo"
        )
        document_1.departments.add(department_1)

        news_article = NewsArticleFactory(
            title="Text content title", content="Text content keywo", author="test"
        )
        matched_sentence = MatchedSentenceFactory(article=news_article)
        matched_sentence.officers.add(officer_1)
        matched_sentence.save()

        rebuild_search_index()

        expected_data = {
            "agencies": {
                "results": [
                    {
                        "id": department_1.agency_slug,
                        "name": department_1.agency_name,
                        "city": department_1.city,
                        "parish": department_1.parish,
                        "location_map_url": department_1.location_map_url,
                    },
                    {
                        "id": department_2.agency_slug,
                        "name": department_2.agency_name,
                        "city": department_2.city,
                        "parish": department_2.parish,
                        "location_map_url": department_2.location_map_url,
                    },
                ],
                "count": 2,
                "next": None,
                "previous": None,
            },
            "officers": {
                "results": [
                    {
                        "id": officer_1.id,
                        "name": officer_1.name,
                        "badges": ["12435"],
                        "departments": [
                            {
                                "id": department_1.agency_slug,
                                "name": department_1.agency_name,
                            }
                        ],
                        "latest_rank": "senior",
                    },
                    {
                        "id": officer_2.id,
                        "name": officer_2.name,
                        "badges": [],
                        "departments": [],
                        "latest_rank": None,
                    },
                ],
                "count": 2,
                "next": None,
                "previous": None,
            },
            "documents": {
                "results": [
                    {
                        "id": document_1.id,
                        "document_type": document_1.document_type,
                        "title": document_1.title,
                        "url": document_1.url,
                        "incident_date": str(document_1.incident_date),
                        "preview_image_url": document_1.preview_image_url,
                        "pages_count": document_1.pages_count,
                        "text_content": document_1.text_content,
                        "text_content_highlight": None,
                        "departments": [
                            {
                                "id": department_1.agency_slug,
                                "name": department_1.agency_name,
                            },
                        ],
                    },
                    {
                        "id": document_2.id,
                        "document_type": document_2.document_type,
                        "title": document_2.title,
                        "url": document_2.url,
                        "incident_date": str(document_2.incident_date),
                        "preview_image_url": document_2.preview_image_url,
                        "pages_count": document_2.pages_count,
                        "text_content": document_2.text_content,
                        "text_content_highlight": "Text content <em>keywo</em>",
                        "departments": [],
                    },
                ],
                "count": 2,
                "next": None,
                "previous": None,
            },
            "articles": {
                "results": [
                    {
                        "id": news_article.id,
                        "source_name": news_article.source.source_display_name,
                        "title": news_article.title,
                        "url": news_article.url,
                        "date": str(news_article.published_date),
                        "author": news_article.author,
                        "content": news_article.content,
                        "content_highlight": "Text content <em>keywo</em>",
                        "author_highlight": None,
                    },
                ],
                "count": 1,
                "next": None,
                "previous": None,
            },
        }

        result = SearchAllQuery(request).search("keywo", None)

        for search_key, items in result.items():
            result[search_key]["results"] = sorted(
                items["results"], key=itemgetter("id")
            )

        assert result == expected_data

    def test_query_with_doc_type_and_limit(self):
        request = Mock(
            query_params={
                "limit": 1,
                "offset": 0,
            },
            build_absolute_uri=Mock(return_value="http://testserver/api/search/"),
        )
        DepartmentFactory(agency_name="Baton Rouge PD")
        department_1 = DepartmentFactory(agency_name="New Orleans keyword PD")
        DepartmentFactory(agency_name="Orleans keywo PD")

        officer = OfficerFactory(first_name="Kenneth", last_name="Anderson")
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(first_name="David keyword", last_name="Jonesworth")
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis keywords")
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_HIRE,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=5,
            day=4,
        )

        DocumentFactory(title="Document title", text_content="Text content")
        document_1 = DocumentFactory(
            title="Document keyword1",
            text_content="Text content 1",
            incident_date=date(2020, 5, 6),
        )
        document_2 = DocumentFactory(
            title="Document 2", text_content="Text content keywo"
        )
        document_1.departments.add(department_1)

        rebuild_search_index()

        expected_data = {
            "documents": {
                "results": [
                    {
                        "id": document_2.id,
                        "document_type": document_2.document_type,
                        "title": document_2.title,
                        "url": document_2.url,
                        "incident_date": str(document_2.incident_date),
                        "preview_image_url": document_2.preview_image_url,
                        "pages_count": document_2.pages_count,
                        "text_content": document_2.text_content,
                        "text_content_highlight": "Text content <em>keywo</em>",
                        "departments": [],
                    },
                ],
                "count": 2,
                "next": "http://testserver/api/search/?limit=1&offset=1",
                "previous": None,
            }
        }

        result = SearchAllQuery(request).search("keywo", "documents")

        for search_key, items in result.items():
            result[search_key]["results"] = sorted(
                items["results"], key=itemgetter("id")
            )

        assert result == expected_data

    def test_query_with_related_officers(self):
        request = Mock(
            query_params={
                "limit": 2,
                "offset": 0,
            }
        )
        DepartmentFactory(agency_name="Baton Rouge PD")
        department_1 = DepartmentFactory(agency_name="New Orleans keyword PD")
        department_2 = DepartmentFactory(agency_name="Orleans keywo PD")

        OfficerFactory(first_name="Kenneth", last_name="Anderson")
        officer_1 = OfficerFactory(
            first_name="David keyword", last_name="Jonesworth", department=department_1
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(
            first_name="Anthony", last_name="Davis keywords", department=department_1
        )
        person_1.officers.add(officer_2)
        person_1.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_HIRE,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=5,
            day=4,
        )

        EventFactory(
            department=department_1,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        EventFactory(
            department=department_1,
            officer=officer_2,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )

        DocumentFactory(title="Document title", text_content="Text content")
        document_1 = DocumentFactory(
            title="Document keyword1",
            text_content="Text content 1",
            incident_date=date(2020, 5, 6),
        )
        document_2 = DocumentFactory(
            title="Document 2", text_content="Text content keywo"
        )
        document_1.departments.add(department_1)

        news_article = NewsArticleFactory(
            title="Text content title", content="Text content keywo", author="test"
        )
        matched_sentence = MatchedSentenceFactory(article=news_article)
        matched_sentence.officers.add(officer_1)
        matched_sentence.save()

        rebuild_search_index()

        expected_data = {
            "agencies": {
                "results": [
                    {
                        "id": department_1.agency_slug,
                        "name": department_1.agency_name,
                        "city": department_1.city,
                        "parish": department_1.parish,
                        "location_map_url": department_1.location_map_url,
                    },
                    {
                        "id": department_2.agency_slug,
                        "name": department_2.agency_name,
                        "city": department_2.city,
                        "parish": department_2.parish,
                        "location_map_url": department_2.location_map_url,
                    },
                ],
                "count": 2,
                "next": None,
                "previous": None,
            },
            "officers": {
                "results": [
                    {
                        "id": officer_1.id,
                        "name": officer_1.name,
                        "badges": ["12435"],
                        "departments": [
                            {
                                "id": department_1.agency_slug,
                                "name": department_1.agency_name,
                            }
                        ],
                        "latest_rank": "senior",
                    },
                ],
                "count": 1,
                "next": None,
                "previous": None,
            },
            "documents": {
                "results": [
                    {
                        "id": document_1.id,
                        "document_type": document_1.document_type,
                        "title": document_1.title,
                        "url": document_1.url,
                        "incident_date": str(document_1.incident_date),
                        "preview_image_url": document_1.preview_image_url,
                        "pages_count": document_1.pages_count,
                        "text_content": document_1.text_content,
                        "text_content_highlight": None,
                        "departments": [
                            {
                                "id": department_1.agency_slug,
                                "name": department_1.agency_name,
                            },
                        ],
                    },
                    {
                        "id": document_2.id,
                        "document_type": document_2.document_type,
                        "title": document_2.title,
                        "url": document_2.url,
                        "incident_date": str(document_2.incident_date),
                        "preview_image_url": document_2.preview_image_url,
                        "pages_count": document_2.pages_count,
                        "text_content": document_2.text_content,
                        "text_content_highlight": "Text content <em>keywo</em>",
                        "departments": [],
                    },
                ],
                "count": 2,
                "next": None,
                "previous": None,
            },
            "articles": {
                "results": [
                    {
                        "id": news_article.id,
                        "source_name": news_article.source.source_display_name,
                        "title": news_article.title,
                        "url": news_article.url,
                        "date": str(news_article.published_date),
                        "author": news_article.author,
                        "content": news_article.content,
                        "content_highlight": "Text content <em>keywo</em>",
                        "author_highlight": None,
                    },
                ],
                "count": 1,
                "next": None,
                "previous": None,
            },
        }

        result = SearchAllQuery(request).search("keywo", None)

        for search_key, items in result.items():
            result[search_key]["results"] = sorted(
                items["results"], key=itemgetter("id")
            )

        assert result == expected_data

    def test_query_with_specified_department(self):
        DepartmentFactory(agency_name="Baton Rouge PD")
        department_1 = DepartmentFactory(agency_name="New Orleans keyword PD")

        request = Mock(
            query_params={
                "limit": 2,
                "offset": 0,
                "department": department_1.agency_slug,
            }
        )

        OfficerFactory(first_name="Kenneth", last_name="Anderson")
        officer_1 = OfficerFactory(
            first_name="David keyword",
            last_name="Jonesworth",
            department=department_1,
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis keywords")
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_HIRE,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer_1,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=5,
            day=4,
        )

        EventFactory(
            department=department_1,
            officer=officer_1,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        DocumentFactory(title="Document title", text_content="Text content")
        document_1 = DocumentFactory(
            title="Document keyword1",
            text_content="Text content 1",
            incident_date=date(2020, 5, 6),
        )
        DocumentFactory(title="Document 2", text_content="Text content keywo")
        document_1.departments.add(department_1)

        news_article = NewsArticleFactory(
            title="Text content title", content="Text content keywo", author="test"
        )
        matched_sentence = MatchedSentenceFactory(article=news_article)
        matched_sentence.officers.add(officer_1)
        matched_sentence.save()

        rebuild_search_index()

        expected_data = {
            "agencies": {
                "results": [],
                "count": 0,
                "next": None,
                "previous": None,
            },
            "officers": {
                "results": [
                    {
                        "id": officer_1.id,
                        "name": officer_1.name,
                        "badges": ["12435"],
                        "departments": [
                            {
                                "id": department_1.agency_slug,
                                "name": department_1.agency_name,
                            },
                        ],
                        "latest_rank": "senior",
                    },
                ],
                "count": 1,
                "next": None,
                "previous": None,
            },
            "documents": {
                "results": [
                    {
                        "id": document_1.id,
                        "document_type": document_1.document_type,
                        "title": document_1.title,
                        "url": document_1.url,
                        "incident_date": str(document_1.incident_date),
                        "preview_image_url": document_1.preview_image_url,
                        "pages_count": document_1.pages_count,
                        "text_content": document_1.text_content,
                        "text_content_highlight": None,
                        "departments": [
                            {
                                "id": department_1.agency_slug,
                                "name": department_1.agency_name,
                            },
                        ],
                    },
                ],
                "count": 1,
                "next": None,
                "previous": None,
            },
            "articles": {
                "results": [
                    {
                        "id": news_article.id,
                        "source_name": news_article.source.source_display_name,
                        "title": news_article.title,
                        "url": news_article.url,
                        "date": str(news_article.published_date),
                        "author": news_article.author,
                        "content": news_article.content,
                        "content_highlight": "Text content <em>keywo</em>",
                        "author_highlight": None,
                    }
                ],
                "count": 1,
                "next": None,
                "previous": None,
            },
        }

        result = SearchAllQuery(request).search(
            "keywo", None, department=department_1.agency_slug
        )

        for search_key, items in result.items():
            result[search_key]["results"] = sorted(
                items["results"], key=itemgetter("id")
            )

        assert result == expected_data
