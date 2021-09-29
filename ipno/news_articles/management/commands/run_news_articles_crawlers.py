from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import F
from django.utils import timezone

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from data.models import WrglRepo
from news_articles.models import NewsArticle
from data.constants import NEWS_ARTICLE_MODEL_NAME
from news_articles.constants import (
    NEWS_ARTICLE_WRGL_COLUMNS,
)
from news_articles.spiders import TheLensNolaScrapyRssSpider
from news_articles.spiders import NolaScrapyRssSpider
from utils.wrgl_generator import WrglGenerator


class Command(BaseCommand):
    def __init__(self):
        self.wrgl = WrglGenerator()

        self.wrgl_repos_mapping = [
            {
                'data': NewsArticle.objects.annotate(
                    source_name=F('source__source_name')
                ).all(),
                'columns': NEWS_ARTICLE_WRGL_COLUMNS,
                'wrgl_repo': settings.NEWS_ARTICLE_WRGL_REPO,
                'wrgl_model_name': NEWS_ARTICLE_MODEL_NAME,
            },
        ]

    def handle(self, *args, **options):
        start_time = timezone.now()

        process = CrawlerProcess(get_project_settings())
        process.crawl(TheLensNolaScrapyRssSpider)
        process.crawl(NolaScrapyRssSpider)

        process.start()

        self.commit_data_to_wrgl(start_time)

    def commit_data_to_wrgl(self, start_time):
        for item in self.wrgl_repos_mapping:
            gzexcel = self.wrgl.generate_csv_file(item['data'], item['columns'])

            count_updated_objects = item['data'].filter(created_at__gte=start_time).count()

            if count_updated_objects:
                response = self.wrgl.create_wrgl_commit(
                    item['wrgl_repo'],
                    f'+ {count_updated_objects} object(s)',
                    'id',
                    gzexcel
                )

                commit_hash = response.json()['hash']
                wrgl_repo = WrglRepo.objects.get(data_model=item['wrgl_model_name'])

                if commit_hash and wrgl_repo.commit_hash != commit_hash:
                    wrgl_repo.commit_hash = commit_hash
                    wrgl_repo.save()
