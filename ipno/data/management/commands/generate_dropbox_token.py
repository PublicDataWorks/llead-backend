from django.core.management.base import BaseCommand

from utils.dropbox_utils import DropboxService


class Command(BaseCommand):
    def handle(self, *args, **options):
        DropboxService.generate_dropbox_token()
