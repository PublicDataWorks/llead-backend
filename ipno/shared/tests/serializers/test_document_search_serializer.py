from django.test import TestCase

from elasticsearch_dsl.utils import AttrDict
from mock import Mock

from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from shared.serializers import DocumentSearchSerializer


class DocumentSearchSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory(text_content="Text content")
        department = DepartmentFactory()
        document.departments.add(department)

        es_doc = Mock(
            id=document.id,
            meta=Mock(
                highlight=AttrDict({"text_content": ["<em>text</em> content"]}),
            ),
        )
        setattr(document, "es_doc", es_doc)

        result = DocumentSearchSerializer(document).data

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
                    "id": department.agency_slug,
                    "name": department.agency_name,
                },
            ],
            "text_content": document.text_content,
            "text_content_highlight": "<em>text</em> content",
        }
