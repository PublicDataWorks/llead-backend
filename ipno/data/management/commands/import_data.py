from django.core.cache import cache
from django.core.management import BaseCommand
from django.utils import timezone

import structlog

from data.services import (
    AgencyImporter,
    AppealImporter,
    ComplaintImporter,
    DocumentImporter,
    EventImporter,
    MigrateOfficerMovement,
    OfficerImporter,
    PersonImporter,
    UofCitizenImporter,
    UofImporter,
    UofOfficerImporter,
)
from news_articles.services import ProcessRematchOfficers
from utils.count_data import (
    calculate_complaint_fraction,
    calculate_officer_fraction,
    count_complaints,
)
from utils.data_utils import compute_department_data_period
from utils.search_index import rebuild_search_index

logger = structlog.get_logger("IPNO")


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = timezone.now()

        agency_imported = AgencyImporter().process()
        officer_imported = OfficerImporter().process()
        complaint_imported = ComplaintImporter().process()
        uof_imported = UofImporter().process()
        uof_officer_imported = UofOfficerImporter().process()
        uof_citizen_imported = UofCitizenImporter().process()

        appeal_imported = AppealImporter().process()
        event_imported = EventImporter().process()
        document_imported = DocumentImporter().process()
        person_imported = PersonImporter().process()

        ProcessRematchOfficers(start_time).process()

        if any(
            [
                agency_imported,
                officer_imported,
            ]
        ):
            logger.info("Calculate officer fraction")
            calculate_officer_fraction()

        if any(
            [
                agency_imported,
                officer_imported,
                complaint_imported,
                event_imported,
                person_imported,
            ]
        ):
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
                uof_officer_imported,
                uof_citizen_imported,
                complaint_imported,
                event_imported,
                appeal_imported,
            ]
        ):
            logger.info("Counting department data period")
            compute_department_data_period()

        if any(
            [
                agency_imported,
                officer_imported,
                uof_imported,
                uof_officer_imported,
                uof_citizen_imported,
                complaint_imported,
                event_imported,
                document_imported,
                person_imported,
                appeal_imported,
            ]
        ):
            logger.info("Rebuilding search index")
            rebuild_search_index()

            logger.info("Flushing cache table")
            cache.clear()
