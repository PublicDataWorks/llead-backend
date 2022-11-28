from unittest.mock import MagicMock, patch

from django.test.testcases import TestCase
from structlog.testing import capture_logs

from utils.task_utils import run_task, check_app_ping


class TaskUtilsTestCase(TestCase):
    @patch('utils.task_utils.check_app_ping', return_value=True)
    def test_run_task_by_celery(self, mock_check_app_ping):
        def func_call(*args, **kwargs):
            return 'test'

        mock_func_call = MagicMock(return_value='test')
        mock_func_call.delay.side_effect = func_call

        task_wrapper = run_task(mock_func_call)
        task_wrapper()

        mock_func_call.assert_not_called()
        mock_func_call.delay.assert_called()

    @patch('utils.task_utils.check_app_ping', return_value=False)
    def test_run_task_directly(self, mock_check_app_ping):
        def func_call(*args, **kwargs):
            return 'test'

        mock_func_call = MagicMock(return_value='test')
        mock_func_call.delay.side_effect = func_call

        task_wrapper = run_task(mock_func_call)
        task_wrapper()

        mock_func_call.assert_called()
        mock_func_call.delay.assert_not_called()

    @patch('utils.task_utils.app')
    def test_check_app_ping_truthy(self, mock_celery_app):
        check_app_ping.cache_clear()
        with capture_logs() as cap_logs:
            mock_celery_app.control.ping.return_value = True
            app_ping = check_app_ping()
        assert not cap_logs
        assert app_ping

    @patch('utils.task_utils.app')
    def test_check_app_ping_falsy(self, mock_celery_app):
        check_app_ping.cache_clear()
        with capture_logs() as cap_logs:
            mock_celery_app.control.ping.return_value = False
            app_ping = check_app_ping()
        assert not app_ping
        assert cap_logs[0]['event'] == 'Celery app is not healthy, please check.'
