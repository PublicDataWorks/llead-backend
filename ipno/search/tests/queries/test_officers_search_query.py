from django.test import TestCase

from officers.factories import OfficerFactory, OfficerHistoryFactory
from departments.factories import DepartmentFactory
from search.queries.officers_search_query import OfficersSearchQuery
from utils.search_index import rebuild_search_index


class OfficersSearchQueryTestCase(TestCase):
    def test_query(self):
        OfficerFactory(first_name='Kenneth', last_name='Anderson')
        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')

        rebuild_search_index()

        result = OfficersSearchQuery().search('Davi')
        officer_ids = {item['id'] for item in result}

        assert officer_ids == {officer_1.id, officer_2.id}

    def test_query_with_matched_by_badges(self):
        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')

        OfficerHistoryFactory(officer=officer_1, badge_no='12435')
        OfficerHistoryFactory(officer=officer_2, badge_no='45812')

        rebuild_search_index()

        result = OfficersSearchQuery().search('45812')
        document_ids = {item['id'] for item in result}

        assert document_ids == {officer_2.id}

    def test_query_with_matched_by_department_names(self):
        officer_1 = OfficerFactory(first_name='David', last_name='Jonesworth')
        officer_2 = OfficerFactory(first_name='Anthony', last_name='Davis')
        officer_3 = OfficerFactory(first_name='Kenneth', last_name='Anderson')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        OfficerHistoryFactory(officer=officer_1, department=department_1, badge_no='12435')
        OfficerHistoryFactory(officer=officer_2, department=department_1, badge_no='45812')
        OfficerHistoryFactory(officer=officer_3, department=department_2, badge_no='45812')

        rebuild_search_index()

        result = OfficersSearchQuery().search('Orlean')
        document_ids = {item['id'] for item in result}

        assert document_ids == {officer_1.id, officer_2.id}
