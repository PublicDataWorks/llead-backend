from django.core.management import BaseCommand

from data.services import OfficerImporter, EventImporter, ComplaintImporter, UofImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        OfficerImporter().process()
        UofImporter().process()
        ComplaintImporter().process()
        EventImporter().process()
