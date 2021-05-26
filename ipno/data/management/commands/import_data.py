from django.core.management import BaseCommand

from data.services import (
    OfficerImporter,
    EventImporter,
    ComplaintImporter,
    UofImporter,
    DocumentImporter,
)
from utils.search_index import rebuild_search_index


class Command(BaseCommand):
    def handle(self, *args, **options):
        officer_imported = OfficerImporter().process()
        complaint_imported = ComplaintImporter().process()
        uof_imported = UofImporter().process()
        event_imported = EventImporter().process()
        document_imported = DocumentImporter().process()

        if any([officer_imported, uof_imported, complaint_imported, event_imported, document_imported]):
            rebuild_search_index()
