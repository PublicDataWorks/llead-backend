from django.conf import settings

from django_elasticsearch_dsl import fields
from django_elasticsearch_dsl.registries import registry

from utils.analyzers import autocomplete_analyzer, search_analyzer, text_analyzer
from utils.es_doc import ESDoc
from utils.es_index import ESIndex

from .models import Document


@registry.register_document
class DocumentESDoc(ESDoc):
    class Index(ESIndex):
        name = f'{"test_" if settings.TEST else ""}documents'

    class Django:
        model = Document
        ignore_signals = True

    def get_indexing_queryset(self):
        return self.get_queryset().prefetch_related(
            "officers",
            "departments",
        )

    id = fields.IntegerField()
    title = fields.TextField(
        analyzer=autocomplete_analyzer, search_analyzer=search_analyzer
    )
    text_content = fields.TextField(
        analyzer=text_analyzer, search_analyzer=search_analyzer
    )
    officer_names = fields.TextField(
        analyzer=autocomplete_analyzer, search_analyzer=search_analyzer
    )
    officer_badges = fields.TextField()
    department_ids = fields.IntegerField()
    department_names = fields.TextField(
        analyzer=autocomplete_analyzer, search_analyzer=search_analyzer
    )
    department_slugs = fields.TextField()

    def prepare_officer_names(self, instance):
        return [officer.name for officer in instance.officers.all()]

    def prepare_officer_badges(self, instance):
        return [officer.badges for officer in instance.officers.all()]

    def prepare_department_names(self, instance):
        return [department.name for department in instance.departments.all()]

    def prepare_department_ids(self, instance):
        return [department.id for department in instance.departments.all()]

    def prepare_department_slugs(self, instance):
        return [department.slug for department in instance.departments.all()]
