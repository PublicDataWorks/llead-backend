from django.conf import settings
from django_elasticsearch_dsl import fields

from django_elasticsearch_dsl.registries import registry

from .models import Document
from utils.es_doc import ESDoc
from utils.es_index import ESIndex
from utils.analyzers import autocomplete_analyzer, search_analyzer, text_analyzer


@registry.register_document
class DocumentESDoc(ESDoc):
    class Index(ESIndex):
        name = f'{"test_" if settings.TEST else ""}documents'

    class Django:
        model = Document

    id = fields.IntegerField()
    title = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    text_content = fields.TextField(analyzer=text_analyzer, search_analyzer=search_analyzer)
