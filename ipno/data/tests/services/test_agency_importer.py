from ast import literal_eval
from unittest.mock import MagicMock

from django.conf import settings
from django.test.testcases import TestCase, override_settings

from mock import Mock, patch
from structlog.testing import capture_logs

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from data.models import ImportLog
from data.services import AgencyImporter
from departments.factories import DepartmentFactory
from departments.models import Department


class AgencyImporterTestCase(TestCase):
    def setUp(self):
        self.patcher = patch("data.services.agency_importer.GoogleCloudService")
        self.patcher.start()

        self.header = ["agency_slug", "agency_name", "location"]
        self.agency1_data = [
            "new-orleans-pd",
            "New Orleans PD",
            "(30.9842977, -91.9623327)",
        ]
        self.agency2_data = ["new-orleans-so", "New Orleans SO", ""]
        self.agency3_data = ["kenner-pd", "Kenner PD", "(30.006161, -90.2640043)"]
        self.agency4_data = [
            "bossier-so",
            "Bossier Parish SO",
            "(30.006161, -90.2640043)",
        ]
        self.agency5_data = [
            "louisiana-state-pd",
            "Louisiana State PD",
            "(29.955935, -90.0663388)",
        ]
        self.agency6_data = [
            "baton-rouge-pd",
            "Baton Rouge PD",
            "(29.955935, -90.0663388)",
        ]
        self.agency7_data = ["lafayette-pd", "Lafayette PD", ""]
        self.agency7_dup_data = self.agency7_data.copy()

        self.agencies_data = [
            self.agency1_data,
            self.agency2_data,
            self.agency3_data,
            self.agency4_data,
            self.agency5_data,
            self.agency6_data,
            self.agency7_data,
            self.agency7_dup_data,
        ]

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    @patch("data.services.base_importer.WRGL_USER", "wrgl_user")
    def test_process_successfully(self):
        DepartmentFactory(
            name="New Orleans PD",
            location=(-91.9623327, 30.9842977),
            location_map_url="new-orleans-pd-url",
        )
        DepartmentFactory(
            name="New Orleans Parish Sheriff's Office",
            slug="new-orleans-so",
        )
        DepartmentFactory(name="Kenner PD")
        DepartmentFactory(
            name="Bossier Parish SO",
            slug="bossier-so",
            location=(-90.2640043, 30.006161),
            location_map_url=None,
        )
        DepartmentFactory(name="Louisiana State PD")

        assert Department.objects.count() == 5

        WrglRepoFactory(
            data_model=AgencyImporter.data_model,
            repo_name="agency_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        agency_importer = AgencyImporter()

        agency_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        agency_importer.repo = Mock()
        agency_importer.new_commit = mock_commit

        agency_importer.retrieve_wrgl_data = Mock()

        agency_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        agency_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.agency6_data,
                self.agency7_data,
                self.agency7_dup_data,
            ],
            "deleted_rows": [
                self.agency5_data,
            ],
            "updated_rows": [
                self.agency1_data,
                self.agency2_data,
                self.agency3_data,
                self.agency4_data,
            ],
        }

        agency_importer.process_wrgl_data = Mock(return_value=processed_data)

        def upload_file_side_effect(upload_location, _file_blob):
            return f"{settings.GC_PATH}{upload_location}"

        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        agency_importer.upload_file = mock_upload_file

        with capture_logs() as cap_logs:
            result = agency_importer.process()

        assert not cap_logs
        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == AgencyImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 4
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Department.objects.count() == 6

        agency_importer.retrieve_wrgl_data.assert_called_with("agency_repo")

        check_columns = self.header + ["slug", "name"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_agency1_data = self.agency1_data.copy()
        expected_agency1_data.extend(["new-orleans-pd", "New Orleans PD"])

        expected_agency2_data = self.agency2_data.copy()
        expected_agency2_data.extend(["new-orleans-so", "New Orleans SO"])

        expected_agency3_data = self.agency3_data.copy()
        expected_agency3_data.extend(["kenner-pd", "Kenner PD"])

        expected_agency4_data = self.agency4_data.copy()
        expected_agency4_data.extend(["bossier-so", "Bossier Parish SO"])

        expected_agency6_data = self.agency6_data.copy()
        expected_agency6_data.extend(["baton-rouge-pd", "Baton Rouge PD"])

        expected_agency7_data = self.agency7_data.copy()
        expected_agency7_data.extend(["lafayette-pd", "Lafayette PD"])

        expected_agencies_data = [
            expected_agency1_data,
            expected_agency2_data,
            expected_agency3_data,
            expected_agency4_data,
            expected_agency6_data,
            expected_agency7_data,
        ]

        for agency_data in expected_agencies_data:
            agency = Department.objects.filter(
                slug=agency_data[check_columns_mappings["agency_slug"]]
            ).first()
            assert agency
            field_attrs = [
                "slug",
                "name",
                "location",
            ]

            for attr in field_attrs:
                raw_data = agency_data[check_columns_mappings[attr]]
                if attr == "location":
                    location_data = literal_eval(raw_data)[::-1] if raw_data else None
                    assert getattr(agency, attr) == location_data
                else:
                    assert getattr(agency, attr) == raw_data

    @override_settings(WRGL_API_KEY="wrgl-api-key")
    @patch("data.services.base_importer.WRGL_USER", "wrgl_user")
    def test_process_successfully_with_columns_changed(self):
        DepartmentFactory(
            name="New Orleans PD",
            location=(-91.9623327, 30.9842977),
            location_map_url="new-orleans-pd-url",
        )
        DepartmentFactory(
            name="New Orleans Parish Sheriff's Office",
            slug="new-orleans-so",
        )
        DepartmentFactory(
            name="Kenner PD",
        )
        DepartmentFactory(
            name="Bossier Parish SO",
            slug="bossier-so",
            location=(-90.2640043, 30.006161),
            location_map_url=None,
        )
        DepartmentFactory(name="Louisiana State PD")

        assert Department.objects.count() == 5

        WrglRepoFactory(
            data_model=AgencyImporter.data_model,
            repo_name="agency_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        agency_importer = AgencyImporter()

        agency_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        agency_importer.repo = Mock()
        agency_importer.new_commit = mock_commit

        agency_importer.retrieve_wrgl_data = Mock()

        agency_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header[:2]
        }
        agency_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.agency6_data,
                self.agency7_data,
                self.agency7_dup_data,
            ],
            "deleted_rows": [
                self.agency5_data,
            ],
            "updated_rows": [
                self.agency1_data,
                self.agency2_data,
                self.agency3_data,
                self.agency4_data,
            ],
        }

        agency_importer.process_wrgl_data = Mock(return_value=processed_data)

        def upload_file_side_effect(upload_location, _file_blob):
            return f"{settings.GC_PATH}{upload_location}"

        mock_upload_file = MagicMock(side_effect=upload_file_side_effect)
        agency_importer.upload_file = mock_upload_file

        result = agency_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == AgencyImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 4
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Department.objects.count() == 6

        agency_importer.retrieve_wrgl_data.assert_called_with("agency_repo")

        check_columns = self.header + ["slug", "name"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_agency1_data = self.agency1_data.copy()
        expected_agency1_data.extend(["new-orleans-pd", "New Orleans PD"])

        expected_agency2_data = self.agency2_data.copy()
        expected_agency2_data.extend(["new-orleans-so", "New Orleans SO"])

        expected_agency3_data = self.agency3_data.copy()
        expected_agency3_data.extend(["kenner-pd", "Kenner PD"])

        expected_agency4_data = self.agency4_data.copy()
        expected_agency4_data.extend(["bossier-so", "Bossier Parish SO"])

        expected_agency6_data = self.agency6_data.copy()
        expected_agency6_data.extend(["baton-rouge-pd", "Baton Rouge PD"])

        expected_agency7_data = self.agency7_data.copy()
        expected_agency7_data.extend(["lafayette-pd", "Lafayette PD"])

        expected_agencies_data = [
            expected_agency1_data,
            expected_agency2_data,
            expected_agency3_data,
            expected_agency4_data,
            expected_agency6_data,
            expected_agency7_data,
        ]

        for agency_data in expected_agencies_data:
            agency = Department.objects.filter(
                slug=agency_data[check_columns_mappings["agency_slug"]]
            ).first()
            assert agency
            field_attrs = [
                "slug",
                "name",
                "location",
            ]

            for attr in field_attrs:
                raw_data = agency_data[check_columns_mappings[attr]]
                if attr == "location":
                    location_data = literal_eval(raw_data)[::-1] if raw_data else None
                    assert getattr(agency, attr) == location_data
                else:
                    assert getattr(agency, attr) == raw_data

    def test_delete_non_existed_agency(self):
        WrglRepoFactory(
            data_model=AgencyImporter.data_model,
            repo_name="agency_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        agency_importer = AgencyImporter()

        agency_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        agency_importer.repo = Mock()
        agency_importer.new_commit = mock_commit

        agency_importer.retrieve_wrgl_data = Mock()

        agency_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        agency_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.agency3_data,
            ],
            "updated_rows": [],
        }

        agency_importer.process_wrgl_data = Mock(return_value=processed_data)

        result = agency_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == AgencyImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == "3950bd17edfd805972781ef9fe2c6449"
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at

    def test_upload_file_success(self):
        upload_location = "location"
        file_blob = "file_blob"

        mock_upload_file_from_string = MagicMock()
        agency_importer = AgencyImporter()
        agency_importer.gs = MagicMock(
            upload_file_from_string=mock_upload_file_from_string
        )

        department_image_url = agency_importer.upload_file(upload_location, file_blob)

        mock_upload_file_from_string.assert_called_with(
            upload_location, file_blob, "image/png"
        )

        assert department_image_url == f"{settings.GC_PATH}location"

    def test_upload_file_fail_not_raise_exception(self):
        upload_location = "location"
        file_blob = "file_blob"

        mock_upload_file_from_string = MagicMock()
        mock_upload_file_from_string.side_effect = Exception()
        agency_importer = AgencyImporter()
        agency_importer.gs = MagicMock(
            upload_file_from_string=mock_upload_file_from_string
        )

        department_image_url = agency_importer.upload_file(upload_location, file_blob)

        mock_upload_file_from_string.assert_called_with(
            upload_location, file_blob, "image/png"
        )

        assert department_image_url is None

    def test_raise_exception_when_updating_location(self):
        WrglRepoFactory(
            data_model=AgencyImporter.data_model,
            repo_name="agency_repo",
            commit_hash="bf56dded0b1c4b57f425acb75d48e68c",
        )

        hash = "3950bd17edfd805972781ef9fe2c6449"

        agency_importer = AgencyImporter()

        agency_importer.branch = "main"

        mock_commit = MagicMock()
        mock_commit.table.columns = self.header
        mock_commit.sum = hash

        agency_importer.repo = Mock()
        agency_importer.new_commit = mock_commit

        agency_importer.retrieve_wrgl_data = Mock()

        agency_importer.old_column_mappings = {
            column: self.header.index(column) for column in self.header
        }
        agency_importer.column_mappings = {
            column: self.header.index(column) for column in self.header
        }

        processed_data = {
            "added_rows": [
                self.agency6_data,
            ],
            "deleted_rows": [],
            "updated_rows": [],
        }

        agency_importer.process_wrgl_data = Mock(return_value=processed_data)

        mock_upload_file = MagicMock()
        mock_upload_file.side_effect = ValueError

        agency_importer.upload_file = mock_upload_file

        with capture_logs() as cap_logs:
            agency_importer.process()

        assert cap_logs[0]["event"] == "Error when import department baton-rouge-pd: "
        assert cap_logs[0]["log_level"] == "error"
