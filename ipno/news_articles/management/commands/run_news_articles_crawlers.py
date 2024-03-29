from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import F
from django.utils import timezone

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from data.constants import NEWS_ARTICLE_MODEL_NAME
from data.models import WrglRepo
from news_articles.constants import NEWS_ARTICLE_WRGL_COLUMNS
from news_articles.models import NewsArticle
from news_articles.spiders import (
    AvoyellesTodayScrapyRssSpider,
    BizNewOrleansScrapyRssSpider,
    BossierPressScrapyRssSpider,
    BRProudScrapyRssSpider,
    CapitalCityNewsScrapyRssSpider,
    ConcordiaSentinelScrapyRssSpider,
    DailyAdvertiserScrapyRssSpider,
    HeraldGuideScrapyRssSpider,
    IberianetScrapyRssSpider,
    JambalayaNewsScrapyRssSpider,
    KlaxScrapyRssSpider,
    LouisianaWeeklyScrapyRssSpider,
    LoyolaMaroonScrapyRssSpider,
    MindenPressHeraldScrapyRssSpider,
    MyArkLamissScrapyRssSpider,
    NatchiochesTimesScrapyRssSpider,
    NichollsWorthScrapyRssSpider,
    NolaScrapyRssSpider,
    ReveilleScrapyRssSpider,
    RustonDailyLeaderScrapyRssSpider,
    ShreveportTimesScrapyRssSpider,
    SlidellIndependentScrapyRssSpider,
    TecheTodayScrapyRssSpider,
    TheAcadianaAdvocateScrapyRssSpider,
    TheFranklinSunScrapyRssSpider,
    TheHawkeyeScrapyRssSpider,
    TheLensNolaScrapyRssSpider,
    TheOouachitaCitizenScrapyRssSpider,
    TownTalkScrapyRssSpider,
    TtfMagazineScrapyRssSpider,
    UptownMessengerScrapyRssSpider,
    VermillionTodayScrapyRssSpider,
    WBRZScrapyRssSpider,
    WGNOScrapyRssSpider,
)
from utils.cache_utils import flush_news_article_related_caches
from utils.wrgl_generator import WrglGenerator


class Command(BaseCommand):
    def __init__(self):
        self.wrgl = WrglGenerator()

        self.wrgl_repos_mapping = [
            {
                "data": NewsArticle.objects.annotate(
                    source_name=F("source__source_name")
                ).all(),
                "columns": NEWS_ARTICLE_WRGL_COLUMNS,
                "wrgl_repo": settings.NEWS_ARTICLE_WRGL_REPO,
                "wrgl_model_name": NEWS_ARTICLE_MODEL_NAME,
            },
        ]

    def handle(self, *args, **options):
        start_time = timezone.now()

        process = CrawlerProcess(
            get_project_settings(), install_root_handler=settings.SIMPLE_LOG
        )

        process.crawl(TheLensNolaScrapyRssSpider)
        process.crawl(NolaScrapyRssSpider)
        process.crawl(VermillionTodayScrapyRssSpider)
        process.crawl(TtfMagazineScrapyRssSpider)
        process.crawl(KlaxScrapyRssSpider)
        process.crawl(CapitalCityNewsScrapyRssSpider)
        process.crawl(BRProudScrapyRssSpider)
        process.crawl(HeraldGuideScrapyRssSpider)
        process.crawl(BossierPressScrapyRssSpider)
        process.crawl(MindenPressHeraldScrapyRssSpider)
        process.crawl(TheHawkeyeScrapyRssSpider)
        process.crawl(MyArkLamissScrapyRssSpider)
        process.crawl(NatchiochesTimesScrapyRssSpider)
        process.crawl(IberianetScrapyRssSpider)
        process.crawl(BizNewOrleansScrapyRssSpider)
        process.crawl(JambalayaNewsScrapyRssSpider)
        process.crawl(LouisianaWeeklyScrapyRssSpider)
        process.crawl(LoyolaMaroonScrapyRssSpider)
        process.crawl(WGNOScrapyRssSpider)
        process.crawl(UptownMessengerScrapyRssSpider)
        process.crawl(RustonDailyLeaderScrapyRssSpider)
        process.crawl(SlidellIndependentScrapyRssSpider)
        process.crawl(TecheTodayScrapyRssSpider)
        process.crawl(NichollsWorthScrapyRssSpider)
        process.crawl(TheAcadianaAdvocateScrapyRssSpider)
        process.crawl(ConcordiaSentinelScrapyRssSpider)
        process.crawl(ReveilleScrapyRssSpider)
        process.crawl(TheFranklinSunScrapyRssSpider)
        process.crawl(TheOouachitaCitizenScrapyRssSpider)
        process.crawl(WBRZScrapyRssSpider)
        process.crawl(TownTalkScrapyRssSpider)
        process.crawl(ShreveportTimesScrapyRssSpider)
        process.crawl(DailyAdvertiserScrapyRssSpider)
        process.crawl(AvoyellesTodayScrapyRssSpider)

        process.start()

        self.commit_data_to_wrgl(start_time)

        flush_news_article_related_caches()

    def commit_data_to_wrgl(self, start_time):
        for item in self.wrgl_repos_mapping:
            csv_file = self.wrgl.generate_csv_file(item["data"], item["columns"])

            count_updated_objects = (
                item["data"].filter(created_at__gte=start_time).count()
            )

            if count_updated_objects:
                result = self.wrgl.create_wrgl_commit(
                    f"+ {count_updated_objects} object(s)",
                    ["id"],
                    csv_file,
                    settings.NEWS_ARTICLE_WRGL_REPO,
                )

                commit_hash = result.sum if result else ""
                wrgl_repo = WrglRepo.objects.get(data_model=item["wrgl_model_name"])

                if commit_hash and wrgl_repo.commit_hash != commit_hash:
                    wrgl_repo.commit_hash = commit_hash
                    wrgl_repo.save()
