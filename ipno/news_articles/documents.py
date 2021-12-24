from django.conf import settings
from django_elasticsearch_dsl import fields

from django_elasticsearch_dsl.registries import registry

from departments.models import Department
from officers.models import Officer
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
    department_slugs = fields.TextField()

    def prepare_source_name(self, instance):
        return instance.source.source_display_name if instance.source else ''

    def prepare_department_slugs(self, instance):
        matched_officers = instance.matched_sentences.all().values_list('officers')
        officers = Officer.objects.filter(person__officers__in=matched_officers)
        departments = Department.objects.filter(officer__in=officers).distinct()

        return [department.slug for department in departments]
