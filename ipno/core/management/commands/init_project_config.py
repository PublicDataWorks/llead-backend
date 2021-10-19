from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('create_initial_app_config')
        call_command('create_initial_wrgl_repos')
        call_command('create_initial_news_articles_sources')
        call_command('create_initial_tasks')
