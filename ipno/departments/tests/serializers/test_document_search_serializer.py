from django.test import TestCase

from mock import Mock, patch
from elasticsearch_dsl.utils import AttrDict

from departments.serializers import DocumentSearchSerializer
from documents.factories import DocumentFactory


class DocumentSearchSerializerTestCase(TestCase):
    @patch('shared.serializers.base_document_search_serializer.TEXT_CONTENT_LIMIT', 15)
    def test_data(self):
        document = DocumentFactory(text_content='This is a very long text')

        es_doc = Mock(
            id=document.id,
            meta=Mock(
                highlight=AttrDict({'text_content': ['<em>text</em> content']}),
            ),
        )
        setattr(document, 'es_doc', es_doc)

        result = DocumentSearchSerializer(document).data

        assert result == {
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'incident_date': str(document.incident_date),
            'text_content': 'This is a very ',
            'text_content_highlight': '<em>text</em> content',
        }
