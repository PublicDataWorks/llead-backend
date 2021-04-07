from operator import itemgetter

from django.test import TestCase

from mock import patch

from shared.serializers import DocumentWithTextContentSerializer
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory


class DocumentWithTextContentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        document.departments.add(department_1, department_2)

        result = DocumentWithTextContentSerializer(document).data
        result['departments'] = sorted(result['departments'], key=itemgetter('id'))

        assert result == {
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'preview_image_url': document.preview_image_url,
            'incident_date': str(document.incident_date),
            'pages_count': document.pages_count,
            'text_content': document.text_content,
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

    @patch('shared.serializers.document_with_text_content_serializer.TEXT_CONTENT_LIMIT', 15)
    def test_text_content(self):
        document = DocumentFactory(text_content='This is a very long text')

        result = DocumentWithTextContentSerializer(document).data

        assert result['text_content'] == 'This is a very '
