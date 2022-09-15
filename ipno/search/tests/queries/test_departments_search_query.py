from django.test import TestCase

from departments.factories import DepartmentFactory
from search.queries.departments_search_query import DepartmentsSearchQuery
from utils.search_index import rebuild_search_index


class DepartmentsSearchQueryTestCase(TestCase):
    def test_query(self):
        DepartmentFactory(name='Baton Rouge PD')
        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Orleans PD')

        rebuild_search_index()

        result = DepartmentsSearchQuery('Orlea').search()
        department_ids = {item['id'] for item in result}

        assert department_ids == {department_1.id, department_2.id}

    def test_aliases_query(self):
        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Orleans PD')
        department_3 = DepartmentFactory(name='Baton Rouge PD', aliases=['Orleans'])
        DepartmentFactory(name='Baton PD', aliases=['Lafayette'])

        rebuild_search_index()

        result = DepartmentsSearchQuery('Orlea').search()
        department_ids = {item['id'] for item in result}

        assert department_ids == {department_1.id, department_2.id, department_3.id}
