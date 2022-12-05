from django.test.testcases import TestCase

from config.celery import app
from departments.documents import DepartmentESDoc
from departments.factories import DepartmentFactory
from departments.tasks import rebuild_department_index
from utils.search_index import rebuild_search_index


class DepartmentTaskTestCase(TestCase):
    def setUp(self):
        app.conf.task_always_eager = True

    def test_rebuild_department_index_successfully(self):
        department = DepartmentFactory(id=1, name="Micheal")

        rebuild_search_index()

        department.name = "Alex"
        department.save()

        rebuild_department_index(1)

        es_doc = DepartmentESDoc.get(id=1)
        assert es_doc.name == "Alex"
