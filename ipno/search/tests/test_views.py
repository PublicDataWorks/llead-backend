import datetime
from datetime import date
from operator import itemgetter

from django.urls import reverse
from rest_framework import status

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase
from utils.search_index import rebuild_search_index


class SearchViewSetTestCase(AuthAPITestCase):
    def test_list_success(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans keyword PD')
        department_2 = DepartmentFactory(name='Orleans keywo PD')

        OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_1 = OfficerFactory(first_name='David keyword', last_name='Jonesworth')
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis keywords')
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no='12435',
        )

        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 6)
        )
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keywo')
        document_1.departments.add(department_1)

        source = NewsArticleSourceFactory(source_display_name='Source')
        news_article_1 = NewsArticleFactory(content='Text content keywo', author='Writer Staff', source=source)
        news_article_2 = NewsArticleFactory(
            title='Dummy title',
            author='text keywo',
            source=source,
            published_date=news_article_1.published_date + datetime.timedelta(days=1)
        )
        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_2.officers.add(officer_2)

        rebuild_search_index()

        expected_data = {
            'departments': {
                'results': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                        'city': department_1.city,
                        'parish': department_1.parish,
                        'location_map_url': department_1.location_map_url,
                    },
                    {
                        'id': department_2.slug,
                        'name': department_2.name,
                        'city': department_2.city,
                        'parish': department_2.parish,
                        'location_map_url': department_2.location_map_url,
                    }, ],
                'count': 2,
                'next': None,
                'previous': None,
            },
            'officers': {
                'results': [
                    {
                        'id': officer_1.id,
                        'name': officer_1.name,
                        'badges': ['12435'],
                        'department': {
                            'id': department_1.slug,
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
                'count': 2,
                'next': None,
                'previous': None,
            },
            'documents': {
                'results': [
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
                                'id': department_1.slug,
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
                'count': 2,
                'next': None,
                'previous': None,
            },
            'articles': {
                'results': [
                    {
                        'id': news_article_1.id,
                        'source_name': 'Source',
                        'title': news_article_1.title,
                        'url': news_article_1.url,
                        'date': str(news_article_1.published_date),
                        'author': news_article_1.author,
                        'content': news_article_1.content,
                        'content_highlight': 'Text content <em>keywo</em>',
                        'author_highlight': None
                    },
                    {
                        'id': news_article_2.id,
                        'source_name': 'Source',
                        'title': news_article_2.title,
                        'url': news_article_2.url,
                        'date': str(news_article_2.published_date),
                        'author': news_article_2.author,
                        'content': news_article_2.content,
                        'content_highlight': None,
                        'author_highlight': 'text <em>keywo</em>'
                    },
                ],
                'count': 2,
                'next': None,
                'previous': None,
            },

        }

        response = self.auth_client.get(reverse('api:search-list'), {'q': 'keywo'})
        assert response.status_code == status.HTTP_200_OK

        data = response.data

        for search_key, items in data.items():
            data[search_key]['results'] = sorted(items['results'], key=itemgetter('id'))

        assert data == expected_data

    def test_list_success_with_doc_type_pagination(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans keyword PD')
        DepartmentFactory(name='Orleans keywo PD')

        officer = OfficerFactory(first_name='Kenneth', last_name='Anderson')
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(first_name='David keyword', last_name='Jonesworth')
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        OfficerFactory(first_name='Anthony', last_name='Davis keywords')

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no='12435',
        )

        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 6)
        )
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keywo')
        document_1.departments.add(department_1)

        rebuild_search_index()

        expected_data = {
            'documents': {
                'results': [
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
                'count': 2,
                'next': 'http://testserver/api/search/?doc_type=documents&limit=1&offset=1&q=keywo',
                'previous': None,
            }
        }

        response = self.auth_client.get(reverse('api:search-list'), {
            'q': 'keywo',
            'doc_type': 'documents',
            'limit': 1,
            'offset': 0,
        })
        assert response.status_code == status.HTTP_200_OK

        data = response.data

        for search_key, items in data.items():
            data[search_key]['results'] = sorted(items['results'], key=itemgetter('id'))

        assert data == expected_data

    def test_list_success_with_wrong_doc_type(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans keyword PD')
        department_2 = DepartmentFactory(name='Orleans keywo PD')

        officer = OfficerFactory(first_name='Kenneth', last_name='Anderson')
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(first_name='David keyword', last_name='Jonesworth')
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis keywords')
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no='12435',
        )

        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 6)
        )
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keywo')
        document_1.departments.add(department_1)

        rebuild_search_index()

        expected_data = {
            'departments': {
                'results': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                        'city': department_1.city,
                        'parish': department_1.parish,
                        'location_map_url': department_1.location_map_url,
                    },
                    {
                        'id': department_2.slug,
                        'name': department_2.name,
                        'city': department_2.city,
                        'parish': department_2.parish,
                        'location_map_url': department_2.location_map_url,
                    }, ],
                'count': 2,
                'next': None,
                'previous': None,
            },
            'officers': {
                'results': [
                    {
                        'id': officer_1.id,
                        'name': officer_1.name,
                        'badges': ['12435'],
                        'department': {
                            'id': department_1.slug,
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
                'count': 2,
                'next': None,
                'previous': None,
            },
            'documents': {
                'results': [
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
                                'id': department_1.slug,
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
                'count': 2,
                'next': None,
                'previous': None,
            },
            'articles': {'count': 0, 'next': None, 'previous': None, 'results': []}
        }

        response = self.auth_client.get(reverse('api:search-list'), {'q': 'keywo', 'doc_type': 'document'})
        assert response.status_code == status.HTTP_200_OK

        data = response.data

        for search_key, items in data.items():
            data[search_key]['results'] = sorted(items['results'], key=itemgetter('id'))

        assert data == expected_data

    def test_list_unauthorized(self):
        response = self.client.get(reverse('api:search-list'), {'q': 'keywo'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_success_with_related_officer(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans keyword PD')
        department_2 = DepartmentFactory(name='Orleans keywo PD')

        OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_1 = OfficerFactory(first_name='David keyword', last_name='Jonesworth')
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis keywords')
        person_1.officers.add(officer_2)
        person_1.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no='12435',
        )

        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 6)
        )
        document_2 = DocumentFactory(title='Document 2', text_content='Text content keywo')
        document_1.departments.add(department_1)

        source = NewsArticleSourceFactory(source_display_name='Source')
        news_article_1 = NewsArticleFactory(content='Text content keywo', author='Writer Staff', source=source)
        news_article_2 = NewsArticleFactory(
            title='Dummy title',
            author='text keywo',
            source=source,
            published_date=news_article_1.published_date + datetime.timedelta(days=1)
        )
        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_2.officers.add(officer_2)

        rebuild_search_index()

        expected_data = {
            'departments': {
                'results': [
                    {
                        'id': department_1.slug,
                        'name': department_1.name,
                        'city': department_1.city,
                        'parish': department_1.parish,
                        'location_map_url': department_1.location_map_url,
                    },
                    {
                        'id': department_2.slug,
                        'name': department_2.name,
                        'city': department_2.city,
                        'parish': department_2.parish,
                        'location_map_url': department_2.location_map_url,
                    }, ],
                'count': 2,
                'next': None,
                'previous': None,
            },
            'officers': {
                'results': [
                    {
                        'id': officer_1.id,
                        'name': officer_1.name,
                        'badges': ['12435'],
                        'department': {
                            'id': department_1.slug,
                            'name': department_1.name,
                        },
                    },
                ],
                'count': 1,
                'next': None,
                'previous': None,
            },
            'documents': {
                'results': [
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
                                'id': department_1.slug,
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
                'count': 2,
                'next': None,
                'previous': None,
            },
            'articles': {
                'results': [
                    {
                        'id': news_article_1.id,
                        'source_name': 'Source',
                        'title': news_article_1.title,
                        'url': news_article_1.url,
                        'date': str(news_article_1.published_date),
                        'author': news_article_1.author,
                        'content': news_article_1.content,
                        'content_highlight': 'Text content <em>keywo</em>',
                        'author_highlight': None
                    },
                    {
                        'id': news_article_2.id,
                        'source_name': 'Source',
                        'title': news_article_2.title,
                        'url': news_article_2.url,
                        'date': str(news_article_2.published_date),
                        'author': news_article_2.author,
                        'content': news_article_2.content,
                        'content_highlight': None,
                        'author_highlight': 'text <em>keywo</em>'
                    },
                ],
                'count': 2,
                'next': None,
                'previous': None,
            },

        }

        response = self.auth_client.get(reverse('api:search-list'), {'q': 'keywo'})
        assert response.status_code == status.HTTP_200_OK

        data = response.data

        for search_key, items in data.items():
            data[search_key]['results'] = sorted(items['results'], key=itemgetter('id'))

        assert data == expected_data

    def test_list_success_with_specified_department(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans keyword PD')

        OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_1 = OfficerFactory(first_name='David keyword', last_name='Jonesworth')
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis keywords')
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            officer=officer_1,
            department=department_1,
            badge_no='12435',
        )

        DocumentFactory(title='Document title', text_content='Text content')
        document_1 = DocumentFactory(
            title='Document keyword1',
            text_content='Text content 1',
            incident_date=date(2020, 5, 6)
        )
        DocumentFactory(title='Document 2', text_content='Text content keywo')
        document_1.departments.add(department_1)

        source = NewsArticleSourceFactory(source_display_name='Source')
        news_article_1 = NewsArticleFactory(content='Text content keywo', author='Writer Staff', source=source)
        news_article_2 = NewsArticleFactory(
            title='Dummy title',
            author='text keywo',
            source=source,
            published_date=news_article_1.published_date + datetime.timedelta(days=1)
        )
        matched_sentence_1 = MatchedSentenceFactory(article=news_article_1)
        matched_sentence_2 = MatchedSentenceFactory(article=news_article_2)
        matched_sentence_1.officers.add(officer_1)
        matched_sentence_2.officers.add(officer_2)

        rebuild_search_index()

        expected_data = {
            'departments': {
                'results': [],
                'count': 0,
                'next': None,
                'previous': None,
            },
            'officers': {
                'results': [
                    {
                        'id': officer_1.id,
                        'name': officer_1.name,
                        'badges': ['12435'],
                        'department': {
                            'id': department_1.slug,
                            'name': department_1.name,
                        },
                    },
                ],
                'count': 1,
                'next': None,
                'previous': None,
            },
            'documents': {
                'results': [
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
                                'id': department_1.slug,
                                'name': department_1.name,
                            },
                        ],
                    },
                ],
                'count': 1,
                'next': None,
                'previous': None,
            },
            'articles': {
                'results': [],
                'count': 0,
                'next': None,
                'previous': None,
            },

        }

        response = self.auth_client.get(reverse('api:search-list'), {
            'q': 'keywo',
            'department': department_1.slug,
        })
        assert response.status_code == status.HTTP_200_OK

        data = response.data

        for search_key, items in data.items():
            data[search_key]['results'] = sorted(items['results'], key=itemgetter('id'))

        assert data == expected_data
