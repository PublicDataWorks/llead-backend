from datetime import date
from django.test.testcases import TestCase

from documents.models import Document
from officers.factories import OfficerFactory, OfficerHistoryFactory
from documents.factories import DocumentFactory


class DocumentTestCase(TestCase):
    def test_prefetch_departments(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        OfficerHistoryFactory(
            officer=officer_1,
            start_date=date(2017, 2, 3),
            end_date=date(2018, 2, 3)
        )
        officer_history = OfficerHistoryFactory(
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3)
        )
        OfficerHistoryFactory(
            officer=officer_2,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_1.officers.add(officer_1)
        document_2.officers.add(officer_2)

        documents = Document.objects.prefetch_departments().order_by('id')
        assert documents[0].officers.all()[0].prefetched_officer_histories == [officer_history]
        assert documents[1].officers.all()[0].prefetched_officer_histories == []
