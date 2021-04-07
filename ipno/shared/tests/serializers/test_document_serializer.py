from operator import itemgetter

from django.test import TestCase

from shared.serializers import DocumentSerializer
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory


class DocumentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        document.departments.add(department_1, department_2)

        result = DocumentSerializer(document).data
        result['departments'] = sorted(result['departments'], key=itemgetter('id'))

        assert result == {
            'id': document.id,
            'document_type': document.document_type,
            'title': document.title,
            'url': document.url,
            'preview_image_url': document.preview_image_url,
            'incident_date': str(document.incident_date),
            'pages_count': document.pages_count,
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
