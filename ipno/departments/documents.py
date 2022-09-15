from django.conf import settings
from django_elasticsearch_dsl import fields

from django_elasticsearch_dsl.registries import registry

from .models import Department
from utils.es_doc import ESDoc
from utils.es_index import ESIndex
from utils.analyzers import autocomplete_analyzer, search_analyzer


@registry.register_document
class DepartmentESDoc(ESDoc):
    class Index(ESIndex):
        name = f'{"test_" if settings.TEST else ""}departments'

    class Django:
        model = Department

    id = fields.IntegerField()
    name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    aliases = fields.ListField(fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer))
