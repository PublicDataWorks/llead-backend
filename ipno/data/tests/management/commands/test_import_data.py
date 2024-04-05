from django.core.management import call_command
from django.test import TestCase

from mock import patch


class ImportDataCommandTestCase(TestCase):
    def setUp(self):
        patch("data.services.agency_importer.GoogleCloudService").start()
        patch("data.services.document_importer.GoogleCloudService").start()

    @patch(
        "data.services.article_classification_importer.ArticleClassificationImporter.process"
    )
    @patch(
        "data.services.post_officer_history_importer.PostOfficerHistoryImporter.process"
    )
    @patch("data.services.brady_importer.BradyImporter.process")
    @patch("django.core.cache.cache.clear")
    @patch("utils.data_utils.compute_department_data_period")
    @patch("data.services.migrate_officer_movement.MigrateOfficerMovement.process")
    @patch("utils.count_data.calculate_complaint_fraction")
    @patch("utils.count_data.calculate_officer_fraction")
    @patch("utils.count_data.count_complaints")
    @patch("utils.search_index.rebuild_search_index")
    @patch("data.services.event_importer.EventImporter.process")
    @patch("data.services.complaint_importer.ComplaintImporter.process")
    @patch("data.services.uof_importer.UofImporter.process")
    @patch("data.services.citizen_importer.CitizenImporter.process")
    @patch("data.services.officer_importer.OfficerImporter.process")
    @patch("data.services.document_importer.DocumentImporter.process")
    @patch("data.services.person_importer.PersonImporter.process")
    @patch("data.services.appeal_importer.AppealImporter.process")
    @patch("data.services.agency_importer.AgencyImporter.process")
    @patch(
        "data.services.schema_validation.SchemaValidation.validate_schemas",
        return_value=True,
    )
    def test_call_command(
        self,
        _,
        agency_process_mock,
        appeal_process_mock,
        person_process_mock,
        document_process_mock,
        officer_process_mock,
        uof_process_mock,
        citizen_process_mock,
        complaint_process_mock,
        event_process_mock,
        rebuild_search_index_mock,
        count_complaints_mock,
        calculate_officer_fraction_mock,
        calculate_complaint_fraction_mock,
        migrate_officer_movement_mock,
        compute_department_data_period_mock,
        cache_clear_mock,
        brady_process_mock,
        post_officer_history_process_mock,
        article_classification_process_mock,
    ):
        agency_process_mock.return_value = True
        appeal_process_mock.return_value = True
        person_process_mock.return_value = True
        document_process_mock.return_value = True
        officer_process_mock.return_value = True
        uof_process_mock.return_value = False
        citizen_process_mock.return_value = False
        complaint_process_mock.return_value = True
        event_process_mock.return_value = False
        brady_process_mock.return_value = True
        post_officer_history_process_mock.return_value = True
        article_classification_process_mock.return_value = True
        call_command("import_data")

        agency_process_mock.assert_called()
        appeal_process_mock.assert_called()
        person_process_mock.assert_called()
        document_process_mock.assert_called()
        officer_process_mock.assert_called()
        uof_process_mock.assert_called()
        citizen_process_mock.assert_called()
        complaint_process_mock.assert_called()
        event_process_mock.assert_called()
        rebuild_search_index_mock.assert_called()
        count_complaints_mock.assert_called()
        calculate_officer_fraction_mock.assert_called()
        calculate_complaint_fraction_mock.assert_called()
        migrate_officer_movement_mock.assert_called()
        compute_department_data_period_mock.assert_called()
        cache_clear_mock.assert_called()

    @patch(
        "data.services.article_classification_importer.ArticleClassificationImporter.process"
    )
    @patch(
        "data.services.post_officer_history_importer.PostOfficerHistoryImporter.process"
    )
    @patch("data.services.brady_importer.BradyImporter.process")
    @patch("django.core.cache.cache.clear")
    @patch("utils.data_utils.compute_department_data_period")
    @patch("data.services.migrate_officer_movement.MigrateOfficerMovement.process")
    @patch("utils.count_data.calculate_complaint_fraction")
    @patch("utils.count_data.calculate_officer_fraction")
    @patch("utils.count_data.count_complaints")
    @patch("utils.search_index.rebuild_search_index")
    @patch("data.services.event_importer.EventImporter.process")
    @patch("data.services.complaint_importer.ComplaintImporter.process")
    @patch("data.services.uof_importer.UofImporter.process")
    @patch("data.services.citizen_importer.CitizenImporter.process")
    @patch("data.services.officer_importer.OfficerImporter.process")
    @patch("data.services.document_importer.DocumentImporter.process")
    @patch("data.services.person_importer.PersonImporter.process")
    @patch("data.services.appeal_importer.AppealImporter.process")
    @patch("data.services.agency_importer.AgencyImporter.process")
    @patch(
        "data.services.schema_validation.SchemaValidation.validate_schemas",
        return_value=True,
    )
    def test_call_command_with_no_new_data(
        self,
        _,
        agency_process_mock,
        appeal_process_mock,
        person_process_mock,
        document_process_mock,
        officer_process_mock,
        uof_process_mock,
        citizen_process_mock,
        complaint_process_mock,
        event_process_mock,
        rebuild_search_index_mock,
        count_complaints_mock,
        calculate_officer_fraction_mock,
        calculate_complaint_fraction_mock,
        migrate_officer_movement_mock,
        compute_department_data_period_mock,
        cache_clear_mock,
        brady_process_mock,
        post_officer_history_process_mock,
        article_classification_process_mock,
    ):
        agency_process_mock.return_value = False
        appeal_process_mock.return_value = False
        person_process_mock.return_value = False
        document_process_mock.return_value = False
        officer_process_mock.return_value = False
        uof_process_mock.return_value = False
        citizen_process_mock.return_value = False
        complaint_process_mock.return_value = False
        event_process_mock.return_value = False
        brady_process_mock.return_value = False
        post_officer_history_process_mock.return_value = False
        article_classification_process_mock.return_value = False
        call_command("import_data")

        agency_process_mock.assert_called()
        appeal_process_mock.assert_called()
        person_process_mock.assert_called()
        document_process_mock.assert_called()
        officer_process_mock.assert_called()
        uof_process_mock.assert_called()
        citizen_process_mock.assert_called()
        complaint_process_mock.assert_called()
        event_process_mock.assert_called()
        rebuild_search_index_mock.assert_not_called()
        count_complaints_mock.assert_not_called()
        calculate_officer_fraction_mock.assert_not_called()
        calculate_complaint_fraction_mock.assert_not_called()
        migrate_officer_movement_mock.assert_not_called()
        compute_department_data_period_mock.assert_not_called()
        cache_clear_mock.assert_not_called()

    @patch(
        "data.services.article_classification_importer.ArticleClassificationImporter.process"
    )
    @patch(
        "data.services.post_officer_history_importer.PostOfficerHistoryImporter.process"
    )
    @patch("data.services.brady_importer.BradyImporter.process")
    @patch("django.core.cache.cache.clear")
    @patch("utils.data_utils.compute_department_data_period")
    @patch("data.services.migrate_officer_movement.MigrateOfficerMovement.process")
    @patch("utils.count_data.calculate_complaint_fraction")
    @patch("utils.count_data.calculate_officer_fraction")
    @patch("utils.count_data.count_complaints")
    @patch("utils.search_index.rebuild_search_index")
    @patch("data.services.event_importer.EventImporter.process")
    @patch("data.services.complaint_importer.ComplaintImporter.process")
    @patch("data.services.uof_importer.UofImporter.process")
    @patch("data.services.citizen_importer.CitizenImporter.process")
    @patch("data.services.officer_importer.OfficerImporter.process")
    @patch("data.services.document_importer.DocumentImporter.process")
    @patch("data.services.person_importer.PersonImporter.process")
    @patch("data.services.appeal_importer.AppealImporter.process")
    @patch("data.services.agency_importer.AgencyImporter.process")
    @patch(
        "data.services.schema_validation.SchemaValidation.validate_schemas",
        return_value=False,
    )
    def test_call_command_with_fail_validating(
        self,
        _,
        agency_process_mock,
        appeal_process_mock,
        person_process_mock,
        document_process_mock,
        officer_process_mock,
        uof_process_mock,
        citizen_process_mock,
        complaint_process_mock,
        event_process_mock,
        rebuild_search_index_mock,
        count_complaints_mock,
        calculate_officer_fraction_mock,
        calculate_complaint_fraction_mock,
        migrate_officer_movement_mock,
        compute_department_data_period_mock,
        cache_clear_mock,
        brady_process_mock,
        post_officer_history_process_mock,
        article_classification_process_mock,
    ):
        call_command("import_data")

        agency_process_mock.assert_not_called()
        appeal_process_mock.assert_not_called()
        person_process_mock.assert_not_called()
        document_process_mock.assert_not_called()
        officer_process_mock.assert_not_called()
        uof_process_mock.assert_not_called()
        citizen_process_mock.assert_not_called()
        complaint_process_mock.assert_not_called()
        event_process_mock.assert_not_called()
        rebuild_search_index_mock.assert_not_called()
        count_complaints_mock.assert_not_called()
        calculate_officer_fraction_mock.assert_not_called()
        calculate_complaint_fraction_mock.assert_not_called()
        migrate_officer_movement_mock.assert_not_called()
        compute_department_data_period_mock.assert_not_called()
        cache_clear_mock.assert_not_called()
        brady_process_mock.assert_not_called()
        post_officer_history_process_mock.assert_not_called()
        article_classification_process_mock.assert_not_called()
