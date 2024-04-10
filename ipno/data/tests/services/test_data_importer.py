from django.test import TestCase

from mock import patch

from data.services.data_importer import DataImporter
from ipno.data.constants import (
    AGENCY_MODEL_NAME,
    APPEAL_MODEL_NAME,
    BRADY_MODEL_NAME,
    CITIZEN_MODEL_NAME,
    COMPLAINT_MODEL_NAME,
    DOCUMENT_MODEL_NAME,
    EVENT_MODEL_NAME,
    NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME,
    OFFICER_MODEL_NAME,
    PERSON_MODEL_NAME,
    POST_OFFICE_HISTORY_MODEL_NAME,
    USE_OF_FORCE_MODEL_NAME,
)


class DataImporterTestCase(TestCase):
    def setUp(self):
        patch("data.services.agency_importer.GoogleCloudService").start()
        patch("data.services.document_importer.GoogleCloudService").start()
        self.data_importer = DataImporter()

    @patch("data.services.data_importer.rmtree")
    @patch("data.services.data_importer.GoogleCloudService")
    @patch("data.services.data_importer.ArticleClassificationImporter.process")
    @patch("data.services.data_importer.PostOfficerHistoryImporter.process")
    @patch("data.services.data_importer.BradyImporter.process")
    @patch("data.services.data_importer.cache.clear")
    @patch("data.services.data_importer.compute_department_data_period")
    @patch("data.services.data_importer.MigrateOfficerMovement.process")
    @patch("data.services.data_importer.calculate_complaint_fraction")
    @patch("data.services.data_importer.calculate_officer_fraction")
    @patch("data.services.data_importer.count_complaints")
    @patch("data.services.data_importer.rebuild_search_index")
    @patch("data.services.data_importer.EventImporter.process")
    @patch("data.services.data_importer.ComplaintImporter.process")
    @patch("data.services.data_importer.UofImporter.process")
    @patch("data.services.data_importer.CitizenImporter.process")
    @patch("data.services.data_importer.OfficerImporter.process")
    @patch("data.services.data_importer.DocumentImporter.process")
    @patch("data.services.data_importer.PersonImporter.process")
    @patch("data.services.data_importer.AppealImporter.process")
    @patch("data.services.data_importer.AgencyImporter.process")
    @patch(
        "data.services.data_importer.SchemaValidation.validate_schemas",
        return_value=True,
    )
    def test_execute_successfully(
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
        mock_google_cloud_service,
        rmtree_mock,
    ):
        mock_google_cloud_service.return_value.download_csv_data_sequentially.return_value = {
            AGENCY_MODEL_NAME: "data_agency.csv",
            APPEAL_MODEL_NAME: "data_appeal-hearing.csv",
            PERSON_MODEL_NAME: "data_person.csv",
            DOCUMENT_MODEL_NAME: "data_documents.csv",
            OFFICER_MODEL_NAME: "data_personnel.csv",
            USE_OF_FORCE_MODEL_NAME: "data_use-of-force.csv",
            CITIZEN_MODEL_NAME: "data_citizens.csv",
            COMPLAINT_MODEL_NAME: "data_allegation.csv",
            EVENT_MODEL_NAME: "data_event.csv",
            NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME: (
                "data_news_article_classification.csv"
            ),
            BRADY_MODEL_NAME: "data_brady.csv",
            POST_OFFICE_HISTORY_MODEL_NAME: "data_post-officer-history.csv",
        }
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

        self.data_importer.execute("folder_name")

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

        rmtree_mock.assert_called()

    @patch("data.services.data_importer.rmtree")
    @patch("data.services.data_importer.GoogleCloudService")
    @patch("data.services.data_importer.ArticleClassificationImporter.process")
    @patch("data.services.data_importer.PostOfficerHistoryImporter.process")
    @patch("data.services.data_importer.BradyImporter.process")
    @patch("data.services.data_importer.cache.clear")
    @patch("data.services.data_importer.compute_department_data_period")
    @patch("data.services.data_importer.MigrateOfficerMovement.process")
    @patch("data.services.data_importer.calculate_complaint_fraction")
    @patch("data.services.data_importer.calculate_officer_fraction")
    @patch("data.services.data_importer.count_complaints")
    @patch("data.services.data_importer.rebuild_search_index")
    @patch("data.services.data_importer.EventImporter.process")
    @patch("data.services.data_importer.ComplaintImporter.process")
    @patch("data.services.data_importer.UofImporter.process")
    @patch("data.services.data_importer.CitizenImporter.process")
    @patch("data.services.data_importer.OfficerImporter.process")
    @patch("data.services.data_importer.DocumentImporter.process")
    @patch("data.services.data_importer.PersonImporter.process")
    @patch("data.services.data_importer.AppealImporter.process")
    @patch("data.services.data_importer.AgencyImporter.process")
    @patch(
        "data.services.data_importer.SchemaValidation.validate_schemas",
        return_value=True,
    )
    def test_execute_with_no_new_data(
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
        mock_google_cloud_service,
        rmtree_mock,
    ):
        mock_google_cloud_service.return_value.download_csv_data_sequentially.return_value = {
            AGENCY_MODEL_NAME: "data_agency.csv",
            APPEAL_MODEL_NAME: "data_appeal-hearing.csv",
            PERSON_MODEL_NAME: "data_person.csv",
            DOCUMENT_MODEL_NAME: "data_documents.csv",
            OFFICER_MODEL_NAME: "data_personnel.csv",
            USE_OF_FORCE_MODEL_NAME: "data_use-of-force.csv",
            CITIZEN_MODEL_NAME: "data_citizens.csv",
            COMPLAINT_MODEL_NAME: "data_allegation.csv",
            EVENT_MODEL_NAME: "data_event.csv",
            NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME: (
                "data_news_article_classification.csv"
            ),
            BRADY_MODEL_NAME: "data_brady.csv",
            POST_OFFICE_HISTORY_MODEL_NAME: "data_post-officer-history.csv",
        }
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
        self.data_importer.execute("folder_name")

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

        rmtree_mock.assert_called()

    @patch("data.services.data_importer.rmtree")
    @patch("data.services.data_importer.GoogleCloudService")
    @patch("data.services.data_importer.ArticleClassificationImporter.process")
    @patch("data.services.data_importer.PostOfficerHistoryImporter.process")
    @patch("data.services.data_importer.BradyImporter.process")
    @patch("data.services.data_importer.cache.clear")
    @patch("data.services.data_importer.compute_department_data_period")
    @patch("data.services.data_importer.MigrateOfficerMovement.process")
    @patch("data.services.data_importer.calculate_complaint_fraction")
    @patch("data.services.data_importer.calculate_officer_fraction")
    @patch("data.services.data_importer.count_complaints")
    @patch("data.services.data_importer.rebuild_search_index")
    @patch("data.services.data_importer.EventImporter.process")
    @patch("data.services.data_importer.ComplaintImporter.process")
    @patch("data.services.data_importer.UofImporter.process")
    @patch("data.services.data_importer.CitizenImporter.process")
    @patch("data.services.data_importer.OfficerImporter.process")
    @patch("data.services.data_importer.DocumentImporter.process")
    @patch("data.services.data_importer.PersonImporter.process")
    @patch("data.services.data_importer.AppealImporter.process")
    @patch("data.services.data_importer.AgencyImporter.process")
    @patch(
        "data.services.data_importer.SchemaValidation.validate_schemas",
        return_value=False,
    )
    def test_execute_with_fail_validating(
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
        mock_google_cloud_service,
        rmtree_mock,
    ):
        mock_google_cloud_service.return_value.download_csv_data_sequentially.return_value = {
            AGENCY_MODEL_NAME: "data_agency.csv",
            APPEAL_MODEL_NAME: "data_appeal-hearing.csv",
            PERSON_MODEL_NAME: "data_person.csv",
            DOCUMENT_MODEL_NAME: "data_documents.csv",
            OFFICER_MODEL_NAME: "data_personnel.csv",
            USE_OF_FORCE_MODEL_NAME: "data_use-of-force.csv",
            CITIZEN_MODEL_NAME: "data_citizens.csv",
            COMPLAINT_MODEL_NAME: "data_allegation.csv",
            EVENT_MODEL_NAME: "data_event.csv",
            NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME: (
                "data_news_article_classification.csv"
            ),
            BRADY_MODEL_NAME: "data_brady.csv",
            POST_OFFICE_HISTORY_MODEL_NAME: "data_post-officer-history.csv",
        }
        self.data_importer.execute("folder_name")

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

        rmtree_mock.assert_called()
