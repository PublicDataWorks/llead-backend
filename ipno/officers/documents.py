from django.conf import settings
from django_elasticsearch_dsl import fields
from django.db.models import Prefetch

from django_elasticsearch_dsl.registries import registry

from .models import Officer
from utils.es_doc import ESDoc
from utils.es_index import ESIndex
from utils.analyzers import autocomplete_analyzer, search_analyzer
from departments.models import Department


@registry.register_document
class OfficerESDoc(ESDoc):
    class Index(ESIndex):
        name = f'{"test_" if settings.TEST else ""}officers'

    class Django:
        model = Officer
        ignore_signals = True

    def get_indexing_queryset(self):
        return self.get_queryset().prefetch_related(
            Prefetch(
                'departments',
                queryset=Department.objects.distinct()
            ),
        ).filter(canonical_person__isnull=False)

    id = fields.IntegerField()
    name = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    badges = fields.TextField()
    department_names = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    department_slugs = fields.TextField()

    def prepare_department_names(self, instance):
        return [department.name for department in instance.departments.all()]

    def prepare_department_slugs(self, instance):
        return [department.slug for department in instance.departments.all()]
