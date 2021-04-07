from operator import itemgetter
from datetime import date

from django.test import TestCase

from mock import Mock
from elasticsearch_dsl.utils import AttrDict

from shared.serializers.es_serializers import DocumentsESSerializer
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory


class DocumentsESSerializerTestCase(TestCase):
    def test_serialize(self):
        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory()
        document_3 = DocumentFactory()
        DocumentFactory()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        document_1.departments.add(department_1, department_2)

        docs = [
            Mock(id=document_2.id, meta=None),
            Mock(
                id=document_1.id,
                meta=Mock(
                    highlight=AttrDict({'text_content': ['<em>text</em> content']}),
                ),
            ),
            Mock(id=document_3.id, meta=None),
        ]
        expected_result = [
            {
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'incident_date': str(document_2.incident_date),
                'preview_image_url': document_2.preview_image_url,
                'pages_count': document_2.pages_count,
                'text_content': document_2.text_content,
                'text_content_highlight': None,
                'departments': [],
            },
            {
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'incident_date': str(document_1.incident_date),
                'preview_image_url': document_1.preview_image_url,
                'pages_count': document_1.pages_count,
                'text_content': document_1.text_content,
                'text_content_highlight': '<em>text</em> content',
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
            },
            {
                'id': document_3.id,
                'document_type': document_3.document_type,
                'title': document_3.title,
                'url': document_3.url,
                'incident_date': str(document_3.incident_date),
                'preview_image_url': document_3.preview_image_url,
                'pages_count': document_3.pages_count,
                'text_content': document_3.text_content,
                'text_content_highlight': None,
                'departments': [],
            },
        ]

        result = DocumentsESSerializer(docs).data
        result[1]['departments'] = sorted(result[1]['departments'], key=itemgetter('id'))
        assert result == expected_result
