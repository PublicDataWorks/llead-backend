from celery import shared_task

from departments.documents import DepartmentESDoc
from departments.models import Department
from utils.task_utils import run_task


@run_task
@shared_task
def rebuild_department_index(doc_id):
    department = Department.objects.get(id=doc_id)
    es_doc = DepartmentESDoc.get(id=doc_id)
    es_doc.update(department)
