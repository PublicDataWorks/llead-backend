from django_elasticsearch_dsl import Document


class ESDoc(Document):
    def create_index(self):
        self._index.create()

    def index_data(self, options={}):
        parallel = options.get("parallel")
        qs = self.get_indexing_queryset()
        self.update(qs, parallel=parallel)

    def delete_index(self):
        self._index.delete(ignore=404)

    def rebuild_index(self, options={}):
        self.delete_index()
        self.create_index()
        self.index_data(options)
