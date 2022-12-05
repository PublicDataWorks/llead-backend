from operator import itemgetter

from django.test import TestCase

from mock import patch

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from shared.serializers import DocumentWithTextContentSerializer


class DocumentWithTextContentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")
        document.departments.add(department_1, department_2)

        result = DocumentWithTextContentSerializer(document).data
        result["departments"] = sorted(result["departments"], key=itemgetter("id"))

        assert result == {
            "id": document.id,
            "document_type": document.document_type,
            "title": document.title,
            "url": document.url,
            "preview_image_url": document.preview_image_url,
            "incident_date": str(document.incident_date),
            "pages_count": document.pages_count,
            "text_content": document.text_content,
            "departments": [
                {
                    "id": department_1.slug,
                    "name": department_1.name,
                },
                {
                    "id": department_2.slug,
                    "name": department_2.name,
                },
            ],
        }

    @patch(
        "shared.serializers.document_with_text_content_serializer.TEXT_CONTENT_LIMIT",
        15,
    )
    def test_text_content(self):
        document = DocumentFactory(text_content="This is a very long text")

        result = DocumentWithTextContentSerializer(document).data

        assert result["text_content"] == "This is a very "
