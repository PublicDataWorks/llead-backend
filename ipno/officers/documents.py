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

    id = fields.IntegerField()
    name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
