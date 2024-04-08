from unittest.mock import Mock, call, patch

from django.conf import settings
from django.test import TestCase

from news_articles.management.commands.run_news_articles_crawlers import Command
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


class CommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    @patch(
        "news_articles.management.commands.run_news_articles_crawlers.CrawlerProcess"
    )
    @patch(
        "news_articles.management.commands.run_news_articles_crawlers.get_project_settings"
    )
    @patch(
        "news_articles.management.commands.run_news_articles_crawlers.flush_news_article_related_caches"
    )
    def test_handle(
        self,
        mock_flush_news_article_related_caches,
        mock_get_project_settings,
        mock_crawler_process,
    ):
        mock_get_project_settings.return_value = "settings"
        mock_crawl = Mock()
        mock_start = Mock()
        mock_crawler_process_object = Mock(crawl=mock_crawl, start=mock_start)
        mock_crawler_process.return_value = mock_crawler_process_object

        self.command.handle()

        mock_get_project_settings.assert_called()
        mock_crawler_process.assert_called_with(
            "settings", install_root_handler=settings.SIMPLE_LOG
        )
        calls_similarity = [
            call(TheLensNolaScrapyRssSpider),
            call(NolaScrapyRssSpider),
            call(VermillionTodayScrapyRssSpider),
            call(TtfMagazineScrapyRssSpider),
            call(KlaxScrapyRssSpider),
            call(CapitalCityNewsScrapyRssSpider),
            call(BRProudScrapyRssSpider),
            call(HeraldGuideScrapyRssSpider),
            call(BossierPressScrapyRssSpider),
            call(MindenPressHeraldScrapyRssSpider),
            call(TheHawkeyeScrapyRssSpider),
            call(MyArkLamissScrapyRssSpider),
            call(NatchiochesTimesScrapyRssSpider),
            call(IberianetScrapyRssSpider),
            call(BizNewOrleansScrapyRssSpider),
            call(JambalayaNewsScrapyRssSpider),
            call(LouisianaWeeklyScrapyRssSpider),
            call(LoyolaMaroonScrapyRssSpider),
            call(WGNOScrapyRssSpider),
            call(UptownMessengerScrapyRssSpider),
            call(RustonDailyLeaderScrapyRssSpider),
            call(SlidellIndependentScrapyRssSpider),
            call(TecheTodayScrapyRssSpider),
            call(NichollsWorthScrapyRssSpider),
            call(TheAcadianaAdvocateScrapyRssSpider),
            call(ConcordiaSentinelScrapyRssSpider),
            call(ReveilleScrapyRssSpider),
            call(TheFranklinSunScrapyRssSpider),
            call(TheOouachitaCitizenScrapyRssSpider),
            call(WBRZScrapyRssSpider),
            call(TownTalkScrapyRssSpider),
            call(ShreveportTimesScrapyRssSpider),
            call(DailyAdvertiserScrapyRssSpider),
            call(AvoyellesTodayScrapyRssSpider),
        ]
        mock_crawl.assert_has_calls(calls_similarity)
        mock_start.assert_called()
        mock_flush_news_article_related_caches.assert_called()
