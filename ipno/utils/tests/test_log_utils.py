import pytest
from django.test.testcases import TestCase
from mock import patch

from utils.log_utils import drop_health_check_event


class LogUtilsTestCase(TestCase):
    @patch('utils.log_utils.DropEvent')
    def test_drop_health_check_event_success(self, mock_drop_event):
        event_dict = {
            'request': '/api/status/'
        }

        with pytest.raises(TypeError):
            result = drop_health_check_event(None, None, event_dict)

            mock_drop_event.assert_called()
            assert result == event_dict

    @patch('utils.log_utils.DropEvent')
    def test_not_raise_drop_event(self, mock_drop_event):
        event_dict = {
            'request': '/api/fail/'
        }

        result = drop_health_check_event(None, None, event_dict)

        mock_drop_event.assert_not_called()
        assert result == event_dict
