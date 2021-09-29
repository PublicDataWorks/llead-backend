from django.test.testcases import TestCase

from tasks.factories import TaskFactory, TaskLogFactory


class TaskLogTestCase(TestCase):
    def test_str(selfs):
        task = TaskFactory()
        log = TaskLogFactory(task=task)
        assert str(log) == f'{task.task_name} run on {str(log.created_at.date())}'
