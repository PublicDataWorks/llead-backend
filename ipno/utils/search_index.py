from django_elasticsearch_dsl.registries import registry


def rebuild_search_index(options={}):
    models = registry.get_models()

    for doc in registry.get_documents(models):
        doc().rebuild_index(options)
