from datetime import date

from django.test.testcases import TestCase

from officers.factories import OfficerFactory
from documents.factories import DocumentFactory


class OfficerTestCase(TestCase):
    def test_name(selfs):
        officer = OfficerFactory(first_name='David', last_name='Jonesworth')
        assert officer.name == 'David Jonesworth'

    def test_name_with_empty_first_name(selfs):
        officer = OfficerFactory(first_name=None, last_name='Jonesworth')
        assert officer.name == 'Jonesworth'

    def test_name_with_empty_last_name(selfs):
        officer = OfficerFactory(first_name='David', last_name=None)
        assert officer.name == 'David'

    def test_empty_name(selfs):
        officer = OfficerFactory(first_name=None, last_name=None)
        assert officer.name == ''

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
