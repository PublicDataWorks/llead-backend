from django.test import TestCase

from departments.factories import DepartmentFactory
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from search.queries.officers_search_query import OfficersSearchQuery
from utils.search_index import rebuild_search_index


class OfficersSearchQueryTestCase(TestCase):
    def test_query(self):
        officer = OfficerFactory(
            first_name="Kenneth",
            last_name="Anderson",
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            complaint_fraction=0.3,
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(
            first_name="Anthony",
            last_name="Davis",
            complaint_fraction=0.7,
        )
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        rebuild_search_index()

        result = OfficersSearchQuery("Davi").search()
        officer_ids = [item["id"] for item in result]

        assert officer_ids == [officer_2.id, officer_1.id]

    def test_query_with_related_officers(self):
        officer = OfficerFactory(first_name="Kenneth", last_name="Anderson")
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(first_name="David", last_name="Jonesworth")
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis")
        person_1.officers.add(officer_2)
        person_1.save()

        rebuild_search_index()

        result = OfficersSearchQuery("Davi").search()
        officer_ids = [item["id"] for item in result]

        assert officer_ids == [officer_1.id]

    def test_aliases_query(self):
        officer = OfficerFactory(
            first_name="Kenneth",
            last_name="Anderson",
            complaint_fraction=0.7,
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            complaint_fraction=0.1,
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(
            first_name="Anthony",
            last_name="Davis",
            complaint_fraction=0.2,
        )
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        officer_3 = OfficerFactory(
            first_name="Sean",
            last_name="Anderson",
            aliases=["Dave"],
            complaint_fraction=1.5,
        )
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()

        rebuild_search_index()

        result = OfficersSearchQuery("Dav").search()
        officer_ids = [item["id"] for item in result]

        assert officer_ids == [officer_3.id, officer_2.id, officer_1.id]

    def test_badge_number_query(self):
        officer = OfficerFactory(first_name="Kenneth", last_name="Anderson")
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(first_name="David", last_name="Jonesworth")
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(first_name="Anthony", last_name="Davis")
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            badge_no="113",
            officer=officer,
            year=1998,
        )
        EventFactory(
            badge_no="256",
            officer=officer,
            year=1999,
        )
        EventFactory(
            badge_no="1135",
            officer=officer_1,
            year=1998,
        )
        EventFactory(
            badge_no="111367",
            officer=officer_2,
            year=1998,
        )

        rebuild_search_index()

        result = OfficersSearchQuery("113").search()
        officer_ids = {item["id"] for item in result}

        assert officer_ids == {officer.id}

    def test_badge_number_query_with_same_badge(self):
        officer = OfficerFactory(
            first_name="Kenneth",
            last_name="Anderson",
            complaint_fraction=0.7,
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(first_name="David", last_name="Jonesworth")
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(
            first_name="Anthony",
            last_name="Davis",
            complaint_fraction=0.2,
        )
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        EventFactory(
            badge_no="113",
            officer=officer,
            year=1998,
        )
        EventFactory(
            badge_no="256",
            officer=officer,
            year=1999,
        )
        EventFactory(
            badge_no="1135",
            officer=officer_1,
            year=1998,
        )
        EventFactory(
            badge_no="111367",
            officer=officer_2,
            year=1998,
        )
        EventFactory(
            badge_no="256",
            officer=officer_2,
            year=1998,
        )

        rebuild_search_index()

        result = OfficersSearchQuery("256").search()
        officer_ids = [item["id"] for item in result]

        assert officer_ids == [officer.id, officer_2.id]

    def test_query_with_specific_department(self):
        department = DepartmentFactory()
        officer = OfficerFactory(
            first_name="Kenneth",
            last_name="Anderson",
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            complaint_fraction=0.3,
            department=department,
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(
            first_name="Anthony",
            last_name="Davis",
            complaint_fraction=0.7,
        )
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        officer_3 = OfficerFactory(
            first_name="David",
            last_name="Bradly",
            complaint_fraction=0.7,
            department=department,
        )
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()

        rebuild_search_index()

        result = OfficersSearchQuery("Davi", department=department.slug).search()
        officer_ids = [item["id"] for item in result]

        assert officer_ids == [officer_3.id, officer_1.id]

    def test_query_with_order(self):
        officer = OfficerFactory(
            first_name="Kenneth",
            last_name="Anderson",
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        officer_1 = OfficerFactory(
            first_name="David",
            last_name="Jonesworth",
            complaint_fraction=0.3,
        )
        person_1 = PersonFactory(canonical_officer=officer_1)
        person_1.officers.add(officer_1)
        person_1.save()

        officer_2 = OfficerFactory(
            first_name="Anthony",
            last_name="Davis",
            complaint_fraction=0.7,
        )
        person_2 = PersonFactory(canonical_officer=officer_2)
        person_2.officers.add(officer_2)
        person_2.save()

        officer_3 = OfficerFactory(
            first_name="David",
            last_name="Bradly",
            complaint_fraction=0.9,
        )
        person_3 = PersonFactory(canonical_officer=officer_3)
        person_3.officers.add(officer_3)
        person_3.save()

        rebuild_search_index()

        officer_search_query = OfficersSearchQuery("Davi")
        officer_search_query.query(order="last_name")

        result = officer_search_query.search()
        officer_ids = [item["id"] for item in result]

        assert officer_ids == [officer_3.id, officer_2.id, officer_1.id]
