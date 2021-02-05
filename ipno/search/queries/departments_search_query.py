from .base_search_query import BaseSearchQuery
from departments.documents import DepartmentESDoc


class DepartmentsSearchQuery(BaseSearchQuery):
    document_klass = DepartmentESDoc
    fields = ['name']
