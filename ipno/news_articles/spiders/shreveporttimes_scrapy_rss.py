from django.conf import settings
from scrapy.loader import ItemLoader

from news_articles.constants import SHREVEPORTTIMES_SOURCE
from news_articles.models import NewsArticle, CrawledPost
from news_articles.spiders.base_scrapy_rss import ScrapyRssSpider, RSSItem
from utils.constants import FILE_TYPES
from utils.pdf_creator import ArticlePdfCreator


class ShreveportTimesScrapyRssSpider(ScrapyRssSpider):
    name = SHREVEPORTTIMES_SOURCE
    allowed_domains = [
        'shreveporttimes.com',
        'thenewsstar.com',
    ]
    urls = ['http://rssfeeds.shreveporttimes.com/shreveport/news']
    custom_settings = {
        'LOG_FILE': None if not settings.FLUENT_LOGGING else settings.FLUENT_PYTHON_LOG_FILE,
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self):
        super().__init__()

    def parse_item(self,  response):
        channel_items = response.xpath("//channel/item")
        items = []
        for item in channel_items:
            loader = ItemLoader(item=RSSItem(), selector=item)
            loader.add_xpath('title', './title/text()')
            loader.add_xpath('description', './description/text()')
            loader.add_xpath('link', './guid/text()')
            loader.add_xpath('guid', './guid/text()')
            loader.add_xpath('published_date', './pubDate/text()')
            loader.add_xpath('author', './creator/text()')

            items.append(loader.load_item())

        return items

    def parse_article(self, response):
        title = response.meta.get('title')
        link = response.meta.get('link')
        guid = response.meta.get('guid')
        author = response.meta.get('author')
        published_date = response.meta.get('published_date')

        content_paragraphs = response.css(
            "article>.gnt_ar_b>:not(aside):not(figure):not(a):not(div)"
        ).getall()
        paragraphs = self.parse_paragraphs(content_paragraphs)

        save_crawled_post = True

        text_content = ' '.join([paragraph['content'] for paragraph in paragraphs])

        pdf_buffer = ArticlePdfCreator(
            title=title,
            author=author,
            date=published_date,
            content=paragraphs,
            link=link
        ).build_pdf()

        pdf_location = self.get_upload_pdf_location(published_date, guid)

        uploaded_url = self.upload_file_to_gcloud(pdf_buffer, pdf_location, FILE_TYPES['PDF'])

        if uploaded_url:
            NewsArticle.objects.get_or_create(
                link=link,
                defaults={
                    'source': self.source,
                    'title': title,
                    'content': text_content,
                    'guid': guid,
                    'author': author,
                    'published_date': published_date,
                    'url': uploaded_url,
                }
            )
        else:
            save_crawled_post = False

        if save_crawled_post:
            crawled_post = CrawledPost(source=self.source, post_guid=guid)
            crawled_post.save()

    def parse_guid(self, guid):
        return '-'.join(guid.split('/')[-3:-1])
