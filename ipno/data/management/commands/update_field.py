from django.core.management import BaseCommand

from data.services import DataTroubleshooting


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(DataTroubleshooting().process())
        DataTroubleshooting().process()
