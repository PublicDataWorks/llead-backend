from dateutil.parser import parse

from django.conf import settings
from bs4 import BeautifulSoup
from itemloaders.processors import TakeFirst
import logging
import scrapy
from scrapy import signals

from news_articles.constants import (
    CRAWL_STATUS_ERROR,
    CRAWL_STATUS_FINISHED,
    CRAWL_STATUS_OPENED,
    NEWS_ARTICLE_CLOUD_SPACES,
    TAG_STYLE_MAPPINGS,
    UNPARSED_TAGS,
)
from news_articles.models import (
    CrawledPost,
    CrawlerError,
    CrawlerLog,
    NewsArticle,
    NewsArticleSource,
)
from utils.google_cloud import GoogleCloudService

logger = logging.getLogger(__name__)


class RSSItem(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    guid = scrapy.Field(output_processor=TakeFirst())
    author = scrapy.Field(output_processor=TakeFirst())
    published_date = scrapy.Field(output_processor=TakeFirst())


class ScrapyRssSpider(scrapy.Spider):
    name = None
    allowed_domains = []
    urls = []
    post_guids = []
    guid_pre = ''
    custom_settings = {
        'LOG_FILE': None if not settings.FLUENT_LOGGING else settings.FLUENT_PYTHON_LOG_FILE,
        'LOG_LEVEL': 'INFO'
    }

    def __init__(self):
        self.gcloud = GoogleCloudService()
        if self.name:
            self.source = NewsArticleSource.objects.get(source_name=self.name)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ScrapyRssSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        return spider

    def spider_closed(self, spider, reason):
        crawler_log = CrawlerLog.objects.filter(source__source_name=spider.name).last()

        news_article_count = NewsArticle.objects.filter(
            source__source_name=spider.name,
            created_at__gte=crawler_log.created_at
        ).count()

        crawler_log.created_rows = news_article_count
        crawler_log.error_rows = crawler_log.errors.count()

        if crawler_log.status != CRAWL_STATUS_ERROR:
            crawler_log.status = CRAWL_STATUS_FINISHED

        crawler_log.save()

    def spider_opened(self, spider):
        crawler_log = CrawlerLog(source=spider.source, status=CRAWL_STATUS_OPENED)
        crawler_log.save()

    def spider_error(self, failure, response, spider):
        crawler_log = CrawlerLog.objects.filter(source__source_name=spider.name).last()

        crawler_log.status = CRAWL_STATUS_ERROR
        crawler_log.save()

        error = CrawlerError(
            response_url=response.url,
            response_status_code=response.status,
            error_message=f'Error occurs while crawling data!\n{failure.getTraceback()}',
            log=crawler_log
        )

        error.save()

    def start_requests(self):
        urls = self.urls
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_rss)

    def parse_rss(self, response):
        self.get_crawled_post_guid()
        response.selector.remove_namespaces()

        rss_items = self.parse_item(response)

        for item in rss_items:
            rss_item_link = item['link']
            guid = self.parse_guid(item['guid'])
            published_date = parse(item['published_date']).date()

            if guid not in self.post_guids:
                yield scrapy.Request(
                    url=rss_item_link,
                    callback=self.parse_article,
                    meta={
                        'link': rss_item_link,
                        'guid': guid,
                        'title': item['title'],
                        'author': item.get('author'),
                        'published_date': published_date,
                    }
                )

    def get_crawled_post_guid(self):
        self.post_guids = CrawledPost.objects.filter(
            source__source_name=self.name
        ).order_by(
            '-created_at'
        ).values_list(
            'post_guid',
            flat=True
        )

    def get_upload_pdf_location(self, published_date, record_id):
        file_name = f'{published_date.strftime("%Y-%m-%d")}_{self.name}_{record_id}.pdf'
        return f'{NEWS_ARTICLE_CLOUD_SPACES}/{self.name}/{file_name}'

    def upload_file_to_gcloud(self, buffer, file_location, file_type):
        try:
            self.gcloud.upload_file_from_string(file_location, buffer, file_type)

            return f"{settings.GC_PATH}{file_location}"
        except Exception as e:
            logger.error(e)

    def parse_guid(self, guid):
        return guid.replace(self.guid_pre, '')

    def parse_section(self, paragraph):
        parsed_paragraph = BeautifulSoup(paragraph, "html.parser")
        tag_name = parsed_paragraph.currentTag()[0].name
        text_content = parsed_paragraph.get_text()

        if tag_name in UNPARSED_TAGS:
            return None

        return {
            'style': TAG_STYLE_MAPPINGS.get(tag_name, 'BodyText'),
            'content': text_content,
        }

    def parse_paragraphs(self, content_paragraphs):
        raw_paragraphs = [self.parse_section(paragraph) for paragraph in content_paragraphs]
        paragraphs = [paragraph for paragraph in raw_paragraphs if paragraph is not None]

        return paragraphs

    def parse_item(self, response):
        raise NotImplementedError

    def parse_article(self, response):
        raise NotImplementedError
