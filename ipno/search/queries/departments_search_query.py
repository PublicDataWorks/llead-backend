from elasticsearch_dsl.function import ScriptScore
from elasticsearch_dsl.query import FunctionScore, MultiMatch

from departments.documents import DepartmentESDoc
from shared.queries.base_search_query import BaseSearchQuery


class DepartmentsSearchQuery(BaseSearchQuery):
    document_klass = DepartmentESDoc
    fields = ["agency_name", "aliases"]
    impact_factors = ["officer_fraction"]

    def query(self, order=None):
        search = self.document_klass().search()

        if self.department:
            search = search.query("match_phrase", department_slugs=self.department)

        impact_factor_list = list(
            map(lambda x: "doc['" + x + "'].value", self.impact_factors)
        )
        impact_factor_list.append("_score")
        script = " * ".join(impact_factor_list)

        multi_match = MultiMatch(query=self.q, fields=self.fields, operator="and")
        script = ScriptScore(script=script)

        q = FunctionScore(query=multi_match, functions=[script])

        if not order:
            return search.query(q)
        else:
            return search.sort(order).query(q)
