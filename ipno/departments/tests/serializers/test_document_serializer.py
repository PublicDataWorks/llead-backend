from django.test import TestCase

from departments.serializers import DocumentSerializer
from documents.factories import DocumentFactory


class DocumentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()

        result = DocumentSerializer(document).data

        assert result == {
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'incident_date': str(document.incident_date),
            'preview_image_url': document.preview_image_url,
            'pages_count': document.pages_count,
        }
