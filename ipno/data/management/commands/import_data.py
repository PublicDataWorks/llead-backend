from django.core.management import BaseCommand
from django.utils import timezone

from data.services import (
    OfficerImporter,
    EventImporter,
    ComplaintImporter,
    UofImporter,
    DocumentImporter,
    PersonImporter,
)
from news_articles.services import ProcessRematchOfficers
from utils.count_complaints import count_complaints
from utils.data_utils import compute_department_data_period
from utils.search_index import rebuild_search_index


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = timezone.now()

        officer_imported = OfficerImporter().process()
        complaint_imported = ComplaintImporter().process()
        uof_imported = UofImporter().process()
        event_imported = EventImporter().process()
        document_imported = DocumentImporter().process()
        person_imported = PersonImporter().process()

        ProcessRematchOfficers(start_time).process()

        if any([officer_imported, complaint_imported, event_imported, person_imported]):
            count_complaints()

        if any([officer_imported, uof_imported, complaint_imported, event_imported]):
            compute_department_data_period()

        if any([officer_imported, uof_imported, complaint_imported, event_imported, document_imported, person_imported]):
            rebuild_search_index()
