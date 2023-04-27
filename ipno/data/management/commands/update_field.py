from django.core.management import BaseCommand

from data.services import DataTroubleshooting


class Command(BaseCommand):
    def handle(self, *args, **options):
        DataTroubleshooting(
            data_model="Complaint",
            updated_fields=("coaccusal",),
            table_id="allegation_uid",
        ).process()
