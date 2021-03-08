from datetime import date

from django.test import TestCase

from mock import Mock
from elasticsearch_dsl.utils import AttrDict

from departments.serializers.es_serializers import DocumentsESSerializer
from documents.factories import DocumentFactory


class DocumentsESSerializerTestCase(TestCase):
    def test_serialize(self):
        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory()
        document_3 = DocumentFactory()
        DocumentFactory()

        docs = [
            Mock(id=document_2.id, meta=None),
            Mock(
                id=document_1.id,
                meta=Mock(
                    highlight=AttrDict({'text_content': ['<em>text</em> content']}),
                ),
            ),
            Mock(id=document_3.id, meta=None),
        ]
        expected_result = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'text_content': document_2.text_content,
                'text_content_highlight': None,
            },
            {
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'incident_date': str(document_1.incident_date),
                'text_content': document_1.text_content,
                'text_content_highlight': '<em>text</em> content',
            },
            {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'incident_date': str(document_3.incident_date),
                'text_content': document_3.text_content,
                'text_content_highlight': None,
            },
        ]

        result = DocumentsESSerializer(docs).data
        assert result == expected_result
