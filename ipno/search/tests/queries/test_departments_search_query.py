from django.test import TestCase

from departments.factories import DepartmentFactory
from search.queries.departments_search_query import DepartmentsSearchQuery
from utils.search_index import rebuild_search_index


class DepartmentsSearchQueryTestCase(TestCase):
    def test_query(self):
        DepartmentFactory(name="Baton Rouge PD")
        department_1 = DepartmentFactory(name="Orleans PD", officer_fraction=0.67)
        department_2 = DepartmentFactory(name="New Orleans PD", officer_fraction=1.0)
        department_3 = DepartmentFactory(
            name="New Orleans Parish Sheriff Office", officer_fraction=0.55
        )

        rebuild_search_index()

        result = DepartmentsSearchQuery("Orlea").search()
        department_ids = [item["id"] for item in result]

        assert department_ids == [department_2.id, department_1.id, department_3.id]

    def test_aliases_query(self):
        department_1 = DepartmentFactory(name="Orleans PD", officer_fraction=0.3)
        department_2 = DepartmentFactory(name="New Orleans PD", officer_fraction=0.9)
        department_3 = DepartmentFactory(
            name="Baton Rouge PD", aliases=["Orleans"], officer_fraction=0.2
        )
        DepartmentFactory(name="Baton PD", aliases=["Lafayette"])

        rebuild_search_index()

        result = DepartmentsSearchQuery("Orlea").search()
        department_ids = [item["id"] for item in result]

        assert department_ids == [department_2.id, department_1.id, department_3.id]

    def test_query_with_specified_department(self):
        DepartmentFactory(name="Baton Rouge PD")
        department_1 = DepartmentFactory(name="Orleans PD", officer_fraction=0.67)
        DepartmentFactory(name="New Orleans PD", officer_fraction=1.0)
        DepartmentFactory(
            name="New Orleans Parish Sheriff Office", officer_fraction=0.55
        )

        rebuild_search_index()

        result = DepartmentsSearchQuery("Orlea", department=department_1.slug).search()

        assert not result

    def test_query_with_order(self):
        DepartmentFactory(name="Baton Rouge PD")
        department_1 = DepartmentFactory(name="Orleans PD", officer_fraction=0.67)
        department_2 = DepartmentFactory(name="New Orleans PD", officer_fraction=1.0)
        department_3 = DepartmentFactory(
            name="New Orleans Parish Sheriff Office", officer_fraction=0.55
        )

        rebuild_search_index()

        department_search_query = DepartmentsSearchQuery("Orlea")
        department_search_query.query(order="name")

        result = department_search_query.search()
        department_ids = [item["id"] for item in result]

        assert department_ids == [department_2.id, department_1.id, department_3.id]
