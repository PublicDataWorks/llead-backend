from celery import shared_task

from officers.documents import OfficerESDoc
from officers.models import Officer
from utils.task_utils import run_task


@run_task
@shared_task
def rebuild_officer_index(doc_id):
    officer = Officer.objects.get(id=doc_id)
    es_doc = OfficerESDoc.get(id=doc_id)
    es_doc.update(officer)
