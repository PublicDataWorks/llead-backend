from django.test.testcases import TestCase

from officers.factories import OfficerFactory
from people.factories import PersonFactory


class PersonTestCase(TestCase):
    def test_str(self):
        officer = OfficerFactory()
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        assert str(person) == f'{person.id} - {officer.uid[:5]}'
