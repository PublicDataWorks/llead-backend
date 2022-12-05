from datetime import date

from django.test.testcases import TestCase

from documents.factories import DocumentFactory
from officers.factories import EventFactory, OfficerFactory
from officers.models import Officer


class OfficerTestCase(TestCase):
    def test_name(selfs):
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        assert officer.name == "David Jonesworth"

    def test_name_with_empty_first_name(selfs):
        officer = OfficerFactory(first_name=None, last_name="Jonesworth")
        assert officer.name == "Jonesworth"

    def test_name_with_empty_last_name(selfs):
        officer = OfficerFactory(first_name="David", last_name=None)
        assert officer.name == "David"

    def test_empty_name(selfs):
        officer = OfficerFactory(first_name=None, last_name=None)
        assert officer.name == ""

    def test_str(self):
        officer = OfficerFactory()
        assert str(officer) == f"{officer.name} - {officer.id} - {officer.uid[:5]}"

    def test_badges(self):
        officer = OfficerFactory()
        EventFactory(
            officer=officer,
            badge_no="12435",
            year=2020,
            month=5,
            day=4,
        )
        EventFactory(
            officer=officer,
            badge_no="67893",
            year=2017,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            badge_no="5432",
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            badge_no="12435",
            year=2015,
            month=7,
            day=20,
        )
        EventFactory(
            officer=officer,
            badge_no=None,
            year=2016,
            month=7,
            day=20,
        )

        prefetch_officer = Officer.objects.prefetch_events()[0]

        assert prefetch_officer.badges == ["12435", "67893", "5432"]

    def test_document_years(self):
        officer = OfficerFactory()

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2019, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_3.officers.add(officer)

        assert sorted(officer.document_years) == [2016, 2018, 2019]
