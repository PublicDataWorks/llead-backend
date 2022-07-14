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
        ignore_signals = True

    def get_indexing_queryset(self):
        return self.get_queryset().select_related('department').filter(canonical_person__isnull=False)

    id = fields.IntegerField()
    name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    badges = fields.TextField()
    department_name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    department_slug = fields.TextField()

    def prepare_department_name(self, instance):
        return instance.department.name if instance.department else None

    def prepare_department_slug(self, instance):
        return instance.department.slug if instance.department else None
