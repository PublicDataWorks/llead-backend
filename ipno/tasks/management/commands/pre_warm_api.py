from django.core.management import BaseCommand
from django.utils import timezone

from tasks.models import Task, TaskLog
from tasks.services import APIPreWarmer


class Command(BaseCommand):
    def handle(self, *args, **options):
        task = Task.objects.get(command="pre_warm_api")
        task_log = TaskLog(task=task)
        task_log.finished_at = timezone.now()
        task_log.save()

        pre_warm_api = APIPreWarmer()
        pre_warm_fp_errors = pre_warm_api.pre_warm_front_page_api()
        pre_warm_dp_errors = pre_warm_api.pre_warm_department_api()

        task_log.finished_at = timezone.now()

        error_mgs = "\n".join([*pre_warm_fp_errors, *pre_warm_dp_errors])
        if error_mgs:
            task_log.error_message = error_mgs

        task_log.save()
