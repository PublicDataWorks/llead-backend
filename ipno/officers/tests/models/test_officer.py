from datetime import date

from django.test.testcases import TestCase

from officers.factories import OfficerFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory


class OfficerTestCase(TestCase):
    def test_name(selfs):
        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        assert officer.name == 'David Jonesworth'

    def test_str(self):
        officer = OfficerFactory()
        assert str(officer) == f"{officer.name} - {officer.id}"

    def test_document_years(self):
        officer = OfficerFactory()

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2019, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        assert sorted(officer.document_years) == [2016, 2018, 2019]

    def test_complaint_years(self):
        officer = OfficerFactory()

        complaint_1 = ComplaintFactory(incident_date=date(2012, 5, 4))
        complaint_2 = ComplaintFactory(incident_date=date(2020, 5, 4))
        complaint_3 = ComplaintFactory(incident_date=date(2018, 5, 4))

        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)
        complaint_3.officers.add(officer)

        assert sorted(officer.complaint_years) == [2012, 2018, 2020]
