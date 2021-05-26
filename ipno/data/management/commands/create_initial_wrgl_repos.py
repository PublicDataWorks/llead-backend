from django.core.management.base import BaseCommand
from data.models import WrglRepo
from data.constants import WRGL_REPOS_DEFAULT


class Command(BaseCommand):
    def handle(self, *args, **options):
        for wrgl_repo in WRGL_REPOS_DEFAULT:
            wrgl_repo_object = WrglRepo.objects.filter(repo_name=wrgl_repo['repo_name']).first()
            if not wrgl_repo_object:
                WrglRepo.objects.create(**wrgl_repo)

