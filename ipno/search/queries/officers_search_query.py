from shared.queries.base_search_query import BaseSearchQuery
from officers.documents import OfficerESDoc


class OfficersSearchQuery(BaseSearchQuery):
    document_klass = OfficerESDoc
    fields = ['name']
