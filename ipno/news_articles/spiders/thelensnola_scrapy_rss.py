from scrapy.loader import ItemLoader

from news_articles.constants import THELENSNOLA_SOURCE
from news_articles.models import CrawledPost, NewsArticle
from news_articles.spiders.base_scrapy_rss import RSSItem, ScrapyRssSpider
from utils.constants import FILE_TYPES
from utils.pdf_creator import ArticlePdfCreator


class TheLensNolaScrapyRssSpider(ScrapyRssSpider):
    name = THELENSNOLA_SOURCE
    allowed_domains = ["thelensnola.org"]
    urls = ["https://thelensnola.org/feed/"]
    guid_pre = "https://thelensnola.org/?p="

    def __init__(self):
        super().__init__()

    def parse_item(self, response):
        channel_items = response.xpath("//channel/item")
        items = []
        for item in channel_items:
            loader = ItemLoader(item=RSSItem(), selector=item)
            loader.add_xpath("title", "./title/text()")
            loader.add_xpath("description", "./description/p/text()")
            loader.add_xpath("link", "./link/text()")
            loader.add_xpath("guid", "./guid/text()")
            loader.add_xpath("published_date", "./pubDate/text()")
            loader.add_xpath("author", "./creator/text()")

            items.append(loader.load_item())

        return items

    def parse_article(self, response):
        title = response.meta.get("title")
        link = response.meta.get("link")
        guid = response.meta.get("guid")
        author = response.meta.get("author")
        published_date = response.meta.get("published_date")

        content_paragraphs = response.css(
            "article .entry-content>:not(aside):not(nav)"
        ).getall()
        paragraphs = self.parse_paragraphs(content_paragraphs)

        save_crawled_post = True

        text_content = " ".join([paragraph["content"] for paragraph in paragraphs])

        pdf_buffer = ArticlePdfCreator(
            title=title,
            author=author,
            date=published_date,
            content=paragraphs,
            link=link,
        ).build_pdf()

        pdf_location = self.get_upload_pdf_location(published_date, title)

        uploaded_url = self.upload_file_to_gcloud(
            pdf_buffer, pdf_location, FILE_TYPES["PDF"]
        )

        if uploaded_url:
            news_article_data = NewsArticle(
                source=self.source,
                link=link,
                title=title,
                content=text_content,
                guid=guid,
                author=author,
                published_date=published_date,
                url=uploaded_url,
            )
            news_article_data.save()
        else:
            save_crawled_post = False

        if save_crawled_post:
            crawled_post = CrawledPost(source=self.source, post_guid=guid)
            crawled_post.save()
