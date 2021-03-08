from django.test import TestCase

from mock import Mock, patch
from elasticsearch_dsl.utils import AttrDict

from shared.serializers import BaseDocumentSearchSerializer
from documents.factories import DocumentFactory


class BaseDocumentSearchSerializerTestCase(TestCase):
    @patch('shared.serializers.base_document_search_serializer.TEXT_CONTENT_LIMIT', 15)
    def test_text_content(self):
        document = DocumentFactory(text_content='This is a very long text')

        result = BaseDocumentSearchSerializer(document).data
        assert result == {
            'text_content': 'This is a very ',
            'text_content_highlight': None,
        }

    def test_text_content_highlight(self):
        document = DocumentFactory(text_content='Text content')
        es_doc = Mock(
            id=document.id,
            meta=Mock(
                highlight=AttrDict({'text_content': ['<em>text</em> content']}),
            ),
        )
        setattr(document, 'es_doc', es_doc)

        result = BaseDocumentSearchSerializer(document).data
        assert result == {
            'text_content': 'Text content',
            'text_content_highlight': '<em>text</em> content',
        }

        assert result['text_content_highlight'] == '<em>text</em> content'
