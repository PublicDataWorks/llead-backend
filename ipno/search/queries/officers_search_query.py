from elasticsearch_dsl.function import ScriptScore
from elasticsearch_dsl.query import FunctionScore, MultiMatch

from officers.documents import OfficerESDoc
from shared.queries.base_search_query import BaseSearchQuery


class OfficersSearchQuery(BaseSearchQuery):
    document_klass = OfficerESDoc
    fields = ["name", "aliases", "badges"]
    impact_factors = ["complaint_fraction"]

    def query(self, order=None):
        search = self.document_klass().search()

        if self.department:
            search = search.query("match_phrase", department_slug=self.department)

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
