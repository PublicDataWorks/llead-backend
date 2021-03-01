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

    def get_indexing_queryset(self):
        return self.get_queryset().prefetch_related(
            'officers',
            'departments',
            'officers__officerhistory_set',
            'officers__departments',
        )

    id = fields.IntegerField()
    title = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    text_content = fields.TextField(analyzer=text_analyzer, search_analyzer=search_analyzer)
    officer_names = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)
    officer_badges = fields.TextField()
    department_names = fields.TextField(analyzer=autocomplete_analyzer, search_analyzer=search_analyzer)

    def prepare_officer_names(self, instance):
        return [officer.name for officer in instance.officers.all()]

    def prepare_officer_badges(self, instance):
        return [officer.badges for officer in instance.officers.all()]

    def prepare_department_names(self, instance):
        return [department.name for department in instance.departments.all()] + [
            department.name
            for officer in instance.officers.all()
            for department in officer.departments.all()
        ]
