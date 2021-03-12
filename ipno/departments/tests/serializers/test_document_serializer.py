from django.test import TestCase

from mock import patch

from departments.serializers import DocumentSerializer
from documents.factories import DocumentFactory


class DocumentSerializerTestCase(TestCase):
    @patch('departments.serializers.document_serializer.TEXT_CONTENT_LIMIT', 15)
    def test_data(self):
        document = DocumentFactory(text_content='This is a very long text')

        result = DocumentSerializer(document).data

        assert result == {
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'incident_date': str(document.incident_date),
            'text_content': 'This is a very '
        }
