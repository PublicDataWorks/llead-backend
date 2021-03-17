from rest_framework.pagination import LimitOffsetPagination


class ESPagination(LimitOffsetPagination):
    def paginate_es_query(self, search_query, request):
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        response = search_query.search(self.limit, self.offset)
        self.count = response.hits.total.value
        self.request = request
        return response
