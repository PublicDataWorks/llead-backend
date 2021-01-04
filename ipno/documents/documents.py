from django_elasticsearch_dsl import Text, Document as ESDoc
from django_elasticsearch_dsl.registries import registry
from .models import Document


@registry.register_document
class DocumentESDoc(ESDoc):
    class Index:
        name = 'documents'

    class Django:
        model = Document

        fields = [
            'title',
        ]
