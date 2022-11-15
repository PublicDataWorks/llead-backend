from datetime import datetime

from django.core.management import call_command
from django.conf import settings

import pytest
from freezegun import freeze_time
from django.test import TestCase
from mock import patch
from unittest.mock import MagicMock

from data.constants import MAP_IMAGES_SUB_DIR
from departments.factories import DepartmentFactory


class UpdateLocationImageCommandTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def capfd(self, capfd):
        self.capfd = capfd

    @patch('data.management.commands.update_location_img.generate_map_thumbnail')
    @patch('data.management.commands.update_location_img.GoogleCloudService')
    def test_call_command(
            self,
            mock_gcs,
            mock_generate_map_thumbnail,
    ):
        mock_gcs_object = MagicMock()
        mock_gcs.return_value = mock_gcs_object

        def mock_generate_map_thumbnail_side_effect(lng, lat):
            if lng != -150.2050293:
                return 'generated-image'
            raise ValueError(f'Invalid lng {lng}')

        mock_generate_map_thumbnail.side_effect = mock_generate_map_thumbnail_side_effect

        dep_location = (-93.9737925, 32.7565316)
        dep_err_location = (-150.2050293, 35.7555316)
        dep = DepartmentFactory(location=dep_location, location_map_url=None)
        DepartmentFactory(location=None)
        dep_3 = DepartmentFactory(location=dep_err_location)

        with freeze_time("2021-09-03 8:00:00"):
            current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            call_command('update_location_img')

        upload_location = f'{MAP_IMAGES_SUB_DIR}/{current_time}-{dep.slug}.png'
        mock_gcs_object.upload_file_from_string.assert_called_with(
            upload_location,
            'generated-image',
            'image/png'
        )
        expected_location_map_url = f"{settings.GC_PATH}{upload_location}"

        dep.refresh_from_db()

        assert dep.location_map_url == expected_location_map_url

        out, err = self.capfd.readouterr()
        expected_out = f"Error when update department map, at department {dep_3.id}, {dep_3.slug}:"\
                       " Invalid lng -150.2050293\n"
        assert out == expected_out
