from django.test.testcases import TestCase

from config.celery import app
from departments.factories import DepartmentFactory
from officers.documents import OfficerESDoc
from officers.factories import OfficerFactory
from officers.tasks import rebuild_officer_index
from people.factories import PersonFactory
from utils.search_index import rebuild_search_index


class OfficerTaskTestCase(TestCase):
    def setUp(self):
        app.conf.task_always_eager = True

    def test_rebuild_officer_index_successfully(self):
        department = DepartmentFactory()
        officer = OfficerFactory(
            id=1,
            department=department,
            aliases=['abc']
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        rebuild_search_index()

        officer.aliases = ['def']
        officer.save()

        rebuild_officer_index(1)

        es_doc = OfficerESDoc.get(id=1)
        assert es_doc.aliases == ['def']
