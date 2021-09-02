from django.test.testcases import TestCase

from tasks.factories import TaskFactory


class TaskTestCase(TestCase):
    def test_str(selfs):
        task = TaskFactory(should_run=True)
        assert str(task) == f'{task.task_name} should run'
