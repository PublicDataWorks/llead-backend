from operator import itemgetter

from django.db.models import Prefetch
from django.test import TestCase

from mock import Mock
from elasticsearch_dsl.utils import AttrDict

from documents.models import Document
from officers.models import OfficerHistory
from search.serializers import DocumentSerializer
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class DocumentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        OfficerHistoryFactory(
            department=department_1,
            officer=officer_1,
        )
        OfficerHistoryFactory(
            department=department_2,
            officer=officer_2,
        )
        OfficerHistoryFactory(
            department=department_2,
            officer=officer_3,
        )
        document.officers.add(officer_1, officer_2, officer_3)

        documents = Document.objects.all().prefetch_related(
            Prefetch(
                'officers__officerhistory_set',
                queryset=OfficerHistory.objects.all(),
                to_attr='prefetched_officer_histories'
            )
        )[:1]

        result = DocumentSerializer(documents[0]).data
        result['departments'] = sorted(result['departments'], key=itemgetter('id'))

        assert result == {
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'incident_date': document.incident_date,
            'text_content': document.text_content,
            'text_content_highlight': None,
            'departments': [
                {
                    'id': department_1.id,
                    'name': department_1.name,
                },
                {
                    'id': department_2.id,
                    'name': department_2.name,
                },
            ],
        }

    def test_text_content_highlight(self):
        document = DocumentFactory()
        es_doc = Mock(
            id=document.id,
            meta=Mock(
                highlight=AttrDict({'text_content': ['<em>text</em> content']}),
            ),
        )
        setattr(document, 'es_doc', es_doc)

        result = DocumentSerializer(document).data
        assert result['text_content_highlight'] == '<em>text</em> content'

    def test_empty_text_content_highlight(self):
        document = DocumentFactory()
        es_doc = Mock(
            id=document.id,
            meta=None
        )
        setattr(document, 'es_doc', es_doc)

        result = DocumentSerializer(document).data
        assert result['text_content_highlight'] is None
