from django.test import TestCase

from django.db.models import BooleanField
from django.db.models.expressions import Value

from departments.serializers import DepartmentDocumentSerializer
from documents.factories import DocumentFactory
from documents.models import Document


class DepartmentDocumentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()

        serialized_document = Document.objects.filter(
            id=document.id
        ).annotate(
            is_starred=Value(True, output_field=BooleanField()),
        ).first()

        result = DepartmentDocumentSerializer(serialized_document).data
        assert result == {
            'id': document.id,
            'title': document.title,
            'url': document.url,
            'incident_date': str(document.incident_date),
            'preview_image_url': document.preview_image_url,
            'pages_count': document.pages_count,
            'is_starred': True,
        }
