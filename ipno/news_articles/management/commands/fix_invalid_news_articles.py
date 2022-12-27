from django.conf import settings
from django.core.management import BaseCommand
from django.utils.text import slugify

import structlog
from tqdm import tqdm

from news_articles.constants import NEWS_ARTICLE_CLOUD_SPACES
from news_articles.models import NewsArticle
from utils.google_cloud import GoogleCloudService

logger = structlog.get_logger("IPNO")


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gcloud = GoogleCloudService()

    def _get_gcs_path_from_url(self, raw_url):
        return raw_url.replace(settings.GC_PATH, "")

    def handle(self, *args, **options):
        inv_news = NewsArticle.objects.select_related("source").filter(
            guid__startswith="http", url__contains="_http"
        )

        for news in tqdm(inv_news):
            raw_url = news.url
            file_path = self._get_gcs_path_from_url(raw_url)

            if not self.gcloud.is_object_exists(file_path):
                logger.error(f"invalid exist ${raw_url}")
                return

            file_name = (
                f'{news.published_date.strftime("%Y-%m-%d")}_{slugify(news.title)}.pdf'
            )
            new_file_path = (
                f"{NEWS_ARTICLE_CLOUD_SPACES}/{news.source.source_name}/{file_name}"
            )

            self.gcloud.move_blob_internally(file_path, new_file_path)
            news.url = f"{settings.GC_PATH}{new_file_path}"

        NewsArticle.objects.bulk_update(inv_news, ["url"], 10000)
