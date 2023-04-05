from django.core.management.base import BaseCommand

from data.constants import WRGL_REPOS_DEFAULT
from data.models import WrglRepo


class Command(BaseCommand):
    def handle(self, *args, **options):
        for wrgl_repo in WRGL_REPOS_DEFAULT:
            wrgl_repo_object = WrglRepo.objects.filter(
                repo_name=wrgl_repo["repo_name"]
            ).first()
            if not wrgl_repo_object:
                WrglRepo.objects.create(**wrgl_repo)

        repos = [repo["repo_name"] for repo in WRGL_REPOS_DEFAULT]
        WrglRepo.objects.exclude(repo_name__in=repos).delete()
