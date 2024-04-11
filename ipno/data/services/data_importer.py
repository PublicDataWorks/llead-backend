from shutil import rmtree

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

import structlog

from data.services import (
    AgencyImporter,
    AppealImporter,
    ArticleClassificationImporter,
    BradyImporter,
    CitizenImporter,
    ComplaintImporter,
    DocumentImporter,
    EventImporter,
    MigrateOfficerMovement,
    OfficerImporter,
    PersonImporter,
    PostOfficerHistoryImporter,
    UofImporter,
)
from data.services.schema_validation import SchemaValidation
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
from news_articles.services import ProcessRematchOfficers
from utils.count_data import (
    calculate_complaint_fraction,
    calculate_officer_fraction,
    count_complaints,
)
from utils.data_utils import compute_department_data_period
from utils.google_cloud import GoogleCloudService
from utils.search_index import rebuild_search_index

logger = structlog.get_logger("IPNO")


class DataImporter:
    def execute(self, folder_name):
        gs = GoogleCloudService(
            settings.RAW_DATA_BUCKET_NAME,
        )

        data_mapping = gs.download_csv_data_sequentially(folder_name)

        try:
            is_validating_success = SchemaValidation().validate_schemas(data_mapping)

            if not is_validating_success:
                logger.error("Schema validation failed")
                return

            start_time = timezone.now()

            agency_imported = AgencyImporter(data_mapping[AGENCY_MODEL_NAME]).process()
            officer_imported = OfficerImporter(
                data_mapping[OFFICER_MODEL_NAME]
            ).process()
            ArticleClassificationImporter(
                data_mapping[NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME]
            ).process()
            complaint_imported = ComplaintImporter(
                data_mapping[COMPLAINT_MODEL_NAME]
            ).process()
            brady_imported = BradyImporter(data_mapping[BRADY_MODEL_NAME]).process()
            uof_imported = UofImporter(data_mapping[USE_OF_FORCE_MODEL_NAME]).process()
            citizen_imported = CitizenImporter(
                data_mapping[CITIZEN_MODEL_NAME]
            ).process()

            appeal_imported = AppealImporter(data_mapping[APPEAL_MODEL_NAME]).process()
            event_imported = EventImporter(data_mapping[EVENT_MODEL_NAME]).process()
            document_imported = DocumentImporter(
                data_mapping[DOCUMENT_MODEL_NAME]
            ).process()
            post_officer_history_imported = PostOfficerHistoryImporter(
                data_mapping[POST_OFFICE_HISTORY_MODEL_NAME]
            ).process()
            person_imported = PersonImporter(data_mapping[PERSON_MODEL_NAME]).process()

            ProcessRematchOfficers(start_time).process()

            if any(
                [
                    agency_imported,
                    officer_imported,
                    complaint_imported,
                    event_imported,
                    person_imported,
                    post_officer_history_imported,
                ]
            ):
                logger.info("Calculate officer fraction")
                calculate_officer_fraction()

                logger.info("Counting complaints")
                count_complaints()

                logger.info("Calculate complaint fraction")
                calculate_complaint_fraction()

                logger.info("Migrate officer movements")
                MigrateOfficerMovement().process()

            if any(
                [
                    agency_imported,
                    officer_imported,
                    uof_imported,
                    citizen_imported,
                    complaint_imported,
                    event_imported,
                    appeal_imported,
                    brady_imported,
                ]
            ):
                logger.info("Counting department data period")
                compute_department_data_period()

            if any(
                [
                    agency_imported,
                    officer_imported,
                    uof_imported,
                    citizen_imported,
                    complaint_imported,
                    event_imported,
                    document_imported,
                    person_imported,
                    appeal_imported,
                    brady_imported,
                ]
            ):
                logger.info("Rebuilding search index")
                rebuild_search_index()

                logger.info("Flushing cache table")
                cache.clear()
        except Exception as e:
            logger.error("Failed to import data", error=str(e))
        finally:
            rmtree(f"{settings.CSV_DATA_PATH}/{folder_name}")
