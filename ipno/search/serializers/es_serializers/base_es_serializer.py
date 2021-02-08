from django.db.models import Case, When


class BaseESSerializer(object):
    serializer = None
    model_klass = None

    def get_queryset(self, ids):
        return self.model_klass.objects.filter(id__in=ids)

    def items(self, docs):
        ids = [doc.id for doc in docs]
        docs_mapping = {doc.id: doc for doc in docs}
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        data_items = self.get_queryset(ids).order_by(preserved)
        for item in data_items:
            setattr(item, 'es_doc', docs_mapping[item.id])

        return data_items

    def serialize(self, docs):
        return self.serializer(self.items(docs), many=True).data
