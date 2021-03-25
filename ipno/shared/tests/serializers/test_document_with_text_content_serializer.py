from operator import itemgetter

from django.db.models import Prefetch
from django.test import TestCase

from mock import patch

from documents.models import Document
from officers.models import OfficerHistory
from shared.serializers import DocumentWithTextContentSerializer
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class DocumentWithTextContentSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()

        OfficerHistoryFactory(
            department=department_1,
            officer=officer_1,
        )
        OfficerHistoryFactory(
            department=department_2,
            officer=officer_2,
        )
        OfficerHistoryFactory(
            department=department_2,
            officer=officer_3,
        )
        document.officers.add(officer_1, officer_2, officer_3)

        documents = Document.objects.all().prefetch_related(
            Prefetch(
                'officers__officerhistory_set',
                queryset=OfficerHistory.objects.all(),
                to_attr='prefetched_officer_histories'
            )
        )[:1]

        result = DocumentWithTextContentSerializer(documents[0]).data
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
