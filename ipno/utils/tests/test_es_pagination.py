from django.test.testcases import TestCase

from mock import Mock

from utils.es_pagination import ESPagination


class ESPaginationTestCase(TestCase):
    def test_paginate_es_query(selfs):
        request = Mock()
        request.query_params = {'limit': 20, 'offset': 30}
        search_result = Mock()
        search_result.hits = Mock()
        search_result.hits.total.value = 50
        search_result.__iter__ = Mock(return_value=iter([1, 2, 3]))
        search_query = Mock()
        search_query.search.return_value = search_result

        paginator = ESPagination()
        page = paginator.paginate_es_query(search_query, request)

        search_query.search.assert_called_with(20, 30)

        assert paginator.count == 50
        assert paginator.limit == 20
        assert paginator.offset == 30
        assert paginator.request == request
        assert list(page) == [1, 2, 3]
