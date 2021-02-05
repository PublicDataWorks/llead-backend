from django.test import TestCase

from officers.factories import OfficerFactory
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
