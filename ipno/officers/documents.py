from django.conf import settings
from django_elasticsearch_dsl import fields

from django_elasticsearch_dsl.registries import registry

from .models import Officer
from utils.es_doc import ESDoc
from utils.es_index import ESIndex
from utils.analyzers import autocomplete_analyzer, search_analyzer


@registry.register_document
class OfficerESDoc(ESDoc):
    class Index(ESIndex):
        name = f'{"test_" if settings.TEST else ""}officers'

    class Django:
        model = Officer

    def get_indexing_queryset(self):
        return self.get_queryset().prefetch_related(
            'officerhistory_set',
            'departments',
        )

    id = fields.IntegerField()
    name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    badges = fields.TextField()
    department_names = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)

    def prepare_department_names(self, instance):
        return [department.name for department in instance.departments.all()]
