from django.core.cache import cache

from celery import shared_task

from data.services.data_importer import DataImporter
from ipno.data.constants import IMPORT_TASK_ID_CACHE_KEY


@shared_task
def import_data(folder_name):
    data_importer = DataImporter()
    try:
        data_importer.execute(folder_name)
    except Exception as e:
        raise e
    finally:
        cache.delete(IMPORT_TASK_ID_CACHE_KEY)
