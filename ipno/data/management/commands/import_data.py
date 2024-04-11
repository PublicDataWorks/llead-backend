from django.core.management import BaseCommand

from data.services.data_importer import DataImporter


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("folder_name", type=str, help="Folder name in the bucket")

    def handle(self, *args, **options):
        folder_name = options["folder_name"]

        data_importer = DataImporter()
        data_importer.execute(folder_name)
