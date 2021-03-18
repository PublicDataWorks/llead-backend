from operator import itemgetter

from django.db.models import Prefetch
from django.test import TestCase

from documents.models import Document
from officers.models import OfficerHistory
from shared.serializers import DocumentWithDepartmentsSerializer
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory


class DocumentWithDepartmentsSerializerTestCase(TestCase):
    def test_data(self):
        document = DocumentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        department_3 = DepartmentFactory()

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
        document.departments.add(department_2, department_3)

        documents = Document.objects.all().prefetch_related(
            Prefetch(
                'officers__officerhistory_set',
                queryset=OfficerHistory.objects.all(),
                to_attr='prefetched_officer_histories'
            )
        )[:1]

        result = DocumentWithDepartmentsSerializer(documents[0]).data
        result['departments'] = sorted(result['departments'], key=itemgetter('id'))

        assert result == {
            'departments': [
                {
                    'id': department_1.id,
                    'name': department_1.name,
                },
                {
                    'id': department_2.id,
                    'name': department_2.name,
                },
                {
                    'id': department_3.id,
                    'name': department_3.name,
                },
            ],
        }