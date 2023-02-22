from operator import itemgetter

from django.test import TestCase

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from shared.serializers import DocumentSerializer


class DocumentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()
        department_1 = DepartmentFactory(agency_name="Baton Rouge PD")
        department_2 = DepartmentFactory(agency_name="New Orleans PD")
        document.departments.add(department_1, department_2)

        result = DocumentSerializer(document).data
        result["departments"] = sorted(result["departments"], key=itemgetter("id"))

        assert result == {
            "id": document.id,
            "document_type": document.document_type,
            "title": document.title,
            "url": document.url,
            "preview_image_url": document.preview_image_url,
            "incident_date": str(document.incident_date),
            "pages_count": document.pages_count,
            "departments": [
                {
                    "id": department_1.agency_slug,
                    "name": department_1.agency_name,
                },
                {
                    "id": department_2.agency_slug,
                    "name": department_2.agency_name,
                },
            ],
        }
