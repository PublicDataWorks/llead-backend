from django.core.management import BaseCommand

from data.services import DataTroubleshooting


class Command(BaseCommand):
    def handle(self, *args, **options):
        DataTroubleshooting(
            data_model="Event", updated_fields=("award",), table_id="event_uid"
        ).process()
