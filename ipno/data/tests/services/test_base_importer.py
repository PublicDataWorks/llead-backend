from csv import DictWriter
from io import BytesIO, StringIO

from django.test.testcases import TestCase

import pytest
from mock import Mock
from pytest import raises

from data.constants import (
    IMPORT_LOG_STATUS_ERROR,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_NO_NEW_DATA,
)
from data.models import ImportLog
from data.services import BaseImporter
from data.util import MockDataReconciliation
from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory
from officers.models import Officer
from use_of_forces.factories import UseOfForceFactory

TEST_MODEL_NAME = "TestModelName"


class TestImporter(BaseImporter):
    data_model = TEST_MODEL_NAME


class BaseImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(csv_content, fieldnames=["id", "name"])
        writer.writeheader()
        writer.writerows(
            [
                {
                    "id": "1",
                    "name": "name 1",
                },
                {
                    "id": "2",
                    "name": "name 2",
                },
                {
                    "id": "3",
                    "name": "name 3",
                },
            ]
        )
        self.csv_stream = BytesIO(csv_content.getvalue().encode("utf-8"))
        self.csv_text = csv_content.getvalue()
        self.tbi = TestImporter()

    def test_process_error_while_processing_data(self):
        self.tbi.import_data = Exception()

        with pytest.raises(Exception):
            assert not self.tbi.process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_ERROR
        assert not import_log.commit_hash
        assert "Error occurs while importing data!" in import_log.error_message
        assert import_log.finished_at

    def test_process_no_new_data(self):
        self.tbi.import_data = Mock(return_value=None)
        self.tbi.data_reconciliation = MockDataReconciliation({})

        assert not self.tbi.process()

        self.tbi.import_data.assert_not_called()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_NO_NEW_DATA
        assert not import_log.created_rows
        assert not import_log.updated_rows
        assert not import_log.deleted_rows
        assert not import_log.error_message
        assert import_log.finished_at

    def test_process_successfully(self):
        import_data_result = {
            "created_rows": 2,
            "updated_rows": 0,
            "deleted_rows": 1,
        }

        self.tbi.import_data = Mock(return_value=import_data_result)

        processed_data = {
            "added_rows": [["1", "name 1"], ["3", "name 3"]],
            "deleted_rows": [
                ["2", "name 2"],
            ],
            "updated_rows": [],
            "columns_mapping": {"id": 0, "name": 1},
        }

        self.tbi.data_reconciliation = MockDataReconciliation(processed_data)

        assert self.tbi.process()

        self.tbi.import_data.assert_called_with(processed_data)

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == TEST_MODEL_NAME
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 1
        assert not import_log.commit_hash
        assert not import_log.error_message
        assert import_log.finished_at

    def test_import_data(self):
        with raises(NotImplementedError):
            BaseImporter().import_data([])

    def test_department_mappings(self):
        department_1 = DepartmentFactory(agency_name="New Orleans PD")
        department_2 = DepartmentFactory(agency_name="Baton Rouge PD")

        mappings = BaseImporter().get_department_mappings()

        expected_mappings = {
            department_1.agency_slug: department_1.id,
            department_2.agency_slug: department_2.id,
        }
        assert mappings == expected_mappings

    def test_officer_mappings(self):
        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        mappings = BaseImporter().get_officer_mappings()
        expected_mappings = {
            officer_1.uid: officer_1.id,
            officer_2.uid: officer_2.id,
        }

        assert mappings == expected_mappings

    def test_uof_mappings(self):
        uof_1 = UseOfForceFactory()
        uof_2 = UseOfForceFactory()
        mappings = BaseImporter().get_uof_mappings()
        expected_mappings = {
            uof_1.uof_uid: uof_1.id,
            uof_2.uof_uid: uof_2.id,
        }

        assert mappings == expected_mappings

    def test_parse_row_data(self):
        self.tbi.ATTRIBUTES = ["id", "name", "year", "desc", "uid"]
        self.tbi.NA_ATTRIBUTES = ["desc"]
        self.tbi.INT_ATTRIBUTES = ["year"]

        column_mappings = {"id": 0, "name": 1, "year": 2, "desc": 3}

        row = ["1", "test", "2021", "NA"]

        result = self.tbi.parse_row_data(row, column_mappings)

        expected_result = {"id": "1", "name": "test", "year": 2021, "desc": None}

        assert result == expected_result

    def test_bulk_import(self):
        OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        new_items_attrs = [
            {
                "uid": "abc",
                "first_name": "test_1",
            }
        ]

        self.tbi.UPDATE_ATTRIBUTES = ["first_name"]

        update_items_attrs = [
            {
                "id": officer_3.id,
                "first_name": "test_2",
            }
        ]

        delete_items_ids = [officer_2.id]

        result = self.tbi.bulk_import(
            Officer, new_items_attrs, update_items_attrs, delete_items_ids
        )

        expected_result = {"created_rows": 1, "updated_rows": 1, "deleted_rows": 1}

        assert result == expected_result

    def test_bulk_import_with_cleanup_action(self):
        OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        new_items_attrs = [
            {
                "uid": "abc",
                "first_name": "test_1",
            }
        ]

        self.tbi.UPDATE_ATTRIBUTES = ["first_name"]

        update_items_attrs = [
            {
                "id": officer_3.id,
                "first_name": "test_2",
            }
        ]

        delete_items_ids = [officer_2.id]

        cleanup_action = Mock()

        delete_items_values = list(
            Officer.objects.filter(id__in=[officer_2.id]).values()
        )

        result = self.tbi.bulk_import(
            Officer,
            new_items_attrs,
            update_items_attrs,
            delete_items_ids,
            cleanup_action,
        )

        expected_result = {"created_rows": 1, "updated_rows": 1, "deleted_rows": 1}

        assert result == expected_result

        cleanup_action.assert_called_with(delete_items_values)
