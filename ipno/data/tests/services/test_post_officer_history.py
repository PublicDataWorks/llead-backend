from django.test import TestCase

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models.import_log import ImportLog
from data.services.post_officer_history_importer import PostOfficerHistoryImporter
from data.tests.services.util import MockDataReconciliation
from departments.factories.department_factory import DepartmentFactory
from officers.factories.officer_factory import OfficerFactory
from post_officer_history.factories.post_officer_history_factory import (
    PostOfficerHistoryFactory,
)
from post_officer_history.models.post_officer_history import PostOfficerHistory


class PostOfficerHistoryImporterTestCase(TestCase):
    def setUp(self):
        self.header = [
            field.name
            for field in PostOfficerHistory._meta.fields
            if field.name not in PostOfficerHistory.BASE_FIELDS
            and field.name not in PostOfficerHistory.CUSTOM_FIELDS
        ]

        self.post_officer_history1_data = [
            "officer-uid1",
            "history_id1",
            "New Orleans PD",
            "",
            "03/01/2020",
        ]
        self.post_officer_history2_data = [
            "officer-uid2",
            "history_id2",
            "New Orleans PD",
            "",
            "02/01/2021",
        ]
        self.post_officer_history3_data = [
            "officer-uid3",
            "history_id3",
            "New Orleans PD",
            "",
            "01/01/2020",
        ]
        self.post_officer_history4_data = [
            "officer-uid4",
            "history_id4",
            "New Orleans PD",
            "",
            "12/01/2020",
        ]
        self.post_officer_history5_data = [
            "officer-uid5",
            "history_id5",
            "Baton Rouge PD",
            "",
            "11/01/2020",
        ]
        self.post_officer_history5_dup_data = self.post_officer_history5_data.copy()

    def test_process_successfully(self):
        PostOfficerHistoryFactory(uid="officer-uid1")
        PostOfficerHistoryFactory(uid="officer-uid2")
        PostOfficerHistoryFactory(uid="officer-uid3")

        department_1 = DepartmentFactory(agency_slug="New Orleans PD")
        department_2 = DepartmentFactory(agency_slug="Baton Rouge PD")

        officer_1 = OfficerFactory(uid="officer-uid1")
        officer_2 = OfficerFactory(uid="officer-uid2")
        officer_4 = OfficerFactory(uid="officer-uid4")
        officer_5 = OfficerFactory(uid="officer-uid5")

        assert PostOfficerHistory.objects.count() == 3

        post_officer_history_importer = PostOfficerHistoryImporter("csv_file_path")

        processed_data = {
            "added_rows": [
                self.post_officer_history4_data,
                self.post_officer_history5_data,
                self.post_officer_history5_dup_data,
            ],
            "deleted_rows": [
                self.post_officer_history3_data,
            ],
            "updated_rows": [
                self.post_officer_history1_data,
                self.post_officer_history2_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        post_officer_history_importer.data_reconciliation = MockDataReconciliation(
            processed_data
        )

        result = post_officer_history_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == PostOfficerHistoryImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 2
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert PostOfficerHistory.objects.count() == 4

        check_columns = self.header + ["department_id", "officer_id"]
        check_columns_mappings = {
            column: check_columns.index(column) for column in check_columns
        }

        expected_post_officer_history1_data = self.post_officer_history1_data.copy()
        expected_post_officer_history1_data.append(department_1.id)
        expected_post_officer_history1_data.append(officer_1.id)

        expected_post_officer_history2_data = self.post_officer_history2_data.copy()
        expected_post_officer_history2_data.append(department_1.id)
        expected_post_officer_history2_data.append(officer_2.id)

        expected_post_officer_history4_data = self.post_officer_history4_data.copy()
        expected_post_officer_history4_data.append(department_1.id)
        expected_post_officer_history4_data.append(officer_4.id)

        expected_post_officer_history5_data = self.post_officer_history5_data.copy()
        expected_post_officer_history5_data.append(department_2.id)
        expected_post_officer_history5_data.append(officer_5.id)

        expected_post_officer_historys_data = [
            expected_post_officer_history1_data,
            expected_post_officer_history2_data,
            expected_post_officer_history4_data,
            expected_post_officer_history5_data,
        ]

        for post_officer_history_data in expected_post_officer_historys_data:
            post_officer_history = PostOfficerHistory.objects.filter(
                uid=post_officer_history_data[check_columns_mappings["uid"]]
            ).first()
            assert post_officer_history
            field_attrs = check_columns

            for attr in field_attrs:
                if attr == "hire_date":
                    assert (
                        getattr(post_officer_history, attr).strftime("%m/%d/%Y")
                        == post_officer_history_data[check_columns_mappings[attr]]
                    )
                else:
                    assert getattr(post_officer_history, attr) == (
                        post_officer_history_data[check_columns_mappings[attr]]
                        if post_officer_history_data[check_columns_mappings[attr]]
                        else None
                    )
