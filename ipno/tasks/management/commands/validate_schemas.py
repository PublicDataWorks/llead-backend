from django.core.management import BaseCommand

from schemas.tasks import validate_schemas


class Command(BaseCommand):
    def handle(self, *args, **options):
        validate_schemas()
