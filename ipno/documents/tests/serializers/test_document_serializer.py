from django.test import TestCase

from documents.serializers import DocumentSerializer
from documents.factories import DocumentFactory


class DocumentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()

        result = DocumentSerializer(document).data
        assert result == {
            'id': document.id,
            'title': document.title,
        }
