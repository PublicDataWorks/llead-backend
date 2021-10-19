from django.conf import settings
from django_elasticsearch_dsl import fields

from django_elasticsearch_dsl.registries import registry

from .models import NewsArticle
from utils.es_doc import ESDoc
from utils.es_index import ESIndex
from utils.analyzers import autocomplete_analyzer, search_analyzer, text_analyzer


@registry.register_document
class NewsArticleESDoc(ESDoc):
    class Index(ESIndex):
        name = f'{"test_" if settings.TEST else ""}articles'

    class Django:
        model = NewsArticle
        ignore_signals = True

    def get_queryset(self):
        return self.django.model.objects.filter(
            matched_sentences__officers__isnull=False
        ).order_by(
            '-published_date',
        ).distinct().select_related('source')

    def get_indexing_queryset(self):
        return self.get_queryset()

    id = fields.IntegerField()
    published_date = fields.DateField()
    title = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    content = fields.TextField(analyzer=text_analyzer, search_analyzer=search_analyzer)
    author = fields.TextField(analyzer=text_analyzer, search_analyzer=search_analyzer)
    source_name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)

    def prepare_source_name(self, instance):
        return instance.source.custom_matching_name if instance.source else ''
