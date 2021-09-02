from django.core.management import call_command, BaseCommand
from django.utils import timezone
import logging
import traceback

from tasks.constants import DAILY_TASK
from tasks.models import Task, TaskLog

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        daily_tasks = Task.objects.filter(task_type=DAILY_TASK, should_run=True)

        for daily_task in daily_tasks:
            task_command = daily_task.command

            task_log = TaskLog(task=daily_task)
            task_log.save()

            try:
                call_command(task_command)
                task_log.finished_at = timezone.now()
                task_log.save()
            except Exception:
                traceback_msg = f'Error when running command {task_command}:\n{traceback.format_exc()}'
                logger.error(traceback_msg)
                task_log.error_message = traceback_msg
                task_log.save()
