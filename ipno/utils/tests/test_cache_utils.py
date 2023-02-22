from datetime import datetime
from unittest.mock import MagicMock, Mock

from django.core.cache import cache
from django.test.testcases import TestCase
from django.urls import reverse

import pytz
from freezegun import freeze_time

from departments.factories import DepartmentFactory
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from utils.cache_utils import (
    custom_cache,
    delete_cache,
    flush_news_article_related_caches,
)


class CacheUtilsTestCase(TestCase):
    def test_delete_cache_no_url_kwargs(self):
        pattern = "api:departments-list"
        url = reverse(pattern)

        cache.set(url, "Department 1")
        assert cache.get(url)

        delete_cache(pattern)

        assert not cache.get(url)

    def test_delete_cache_with_url_kwargs(self):
        pattern = "api:departments-detail"
        url_kwargs = {"pk": "slug"}
        url = reverse("api:departments-detail", kwargs=url_kwargs)

        cache.set(url, "Department 1")
        assert cache.get(url)

        delete_cache(pattern, url_kwargs=url_kwargs)

        assert not cache.get(url)

    def test_custom_cache(self):
        pattern = "api:departments-list"
        url = reverse(pattern)

        response = MagicMock()
        response.data = "test"

        def func_call(*args, **kwargs):
            return response

        mock_func_call = Mock(wraps=func_call)

        request = MagicMock()
        request.get_full_path.return_value = url

        view = MagicMock()

        cached_func = custom_cache(mock_func_call)
        result = cached_func(view, request)

        mock_func_call.assert_called_once()
        assert result.data == response.data
        assert cache.get(url) == response.data

        cached_func(view, request)
        mock_func_call.assert_called_once()

    def test_flush_news_article_related_caches_no_start_time(self):
        department = DepartmentFactory(agency_name="New Orleans PD")
        DepartmentFactory()
        DepartmentFactory()

        officer = OfficerFactory(department=department)
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()

        OfficerFactory()
        OfficerFactory()

        source = NewsArticleSourceFactory(source_display_name="Source")
        news_article = NewsArticleFactory(
            content="Text content", author="Writer Staff", source=source
        )
        matched_sentence = MatchedSentenceFactory(article=news_article)
        matched_sentence.officers.add(officer)

        cache.set(reverse("api:news-articles-list"), "News article list")
        cache.set(reverse("api:analytics-summary"), "Summary")
        cache.set(
            reverse("api:officers-timeline", kwargs={"pk": officer.id}), "Timeline"
        )
        cache.set(
            reverse("api:departments-detail", kwargs={"pk": department.agency_slug}),
            "Department detail",
        )
        cache.set(
            reverse(
                "api:departments-news-articles", kwargs={"pk": department.agency_slug}
            ),
            "Department article",
        )
        cache.set(reverse("api:officers-list"), "Officer list")

        flush_news_article_related_caches()

        assert not cache.get(reverse("api:news-articles-list"))
        assert not cache.get(reverse("api:analytics-summary"))
        assert not cache.get(
            reverse("api:officers-timeline", kwargs={"pk": officer.id})
        )
        assert not cache.get(
            reverse("api:departments-detail", kwargs={"pk": department.agency_slug})
        )
        assert not cache.get(
            reverse(
                "api:departments-news-articles", kwargs={"pk": department.agency_slug}
            )
        )
        assert cache.get(reverse("api:officers-list"))

    def test_flush_news_article_related_caches_with_start_time(self):
        department_1 = DepartmentFactory(agency_name="Department 1")
        department_2 = DepartmentFactory(agency_name="Department 2")
        DepartmentFactory()
        DepartmentFactory()

        officer_1 = OfficerFactory(department=department_1)
        officer_2 = OfficerFactory(department=department_2)
        person = PersonFactory(canonical_officer=officer_1)
        person.officers.add(officer_1)
        person.officers.add(officer_2)
        person.save()

        OfficerFactory()
        OfficerFactory()

        source = NewsArticleSourceFactory(source_display_name="Source")
        news_article = NewsArticleFactory(
            content="Text content", author="Writer Staff", source=source
        )

        with freeze_time("2021-09-03 8:00:00"):
            matched_sentence_1 = MatchedSentenceFactory(article=news_article)
            matched_sentence_1.officers.add(officer_1)

        with freeze_time("2021-09-03 10:00:00"):
            matched_sentence_2 = MatchedSentenceFactory(article=news_article)
            matched_sentence_2.officers.add(officer_2)

        cache.set(reverse("api:news-articles-list"), "News article list")
        cache.set(reverse("api:analytics-summary"), "Summary")
        cache.set(
            reverse("api:officers-timeline", kwargs={"pk": officer_1.id}),
            "Timeline of officer 1",
        )
        cache.set(
            reverse("api:officers-timeline", kwargs={"pk": officer_2.id}),
            "Timeline of officer 2",
        )
        cache.set(
            reverse("api:departments-detail", kwargs={"pk": department_1.agency_slug}),
            "Department 1 detail",
        )
        cache.set(
            reverse("api:departments-detail", kwargs={"pk": department_2.agency_slug}),
            "Department 2 detail",
        )
        cache.set(
            reverse(
                "api:departments-news-articles", kwargs={"pk": department_1.agency_slug}
            ),
            "Department 1 article",
        )
        cache.set(
            reverse(
                "api:departments-news-articles", kwargs={"pk": department_2.agency_slug}
            ),
            "Department 1 article",
        )
        cache.set(reverse("api:officers-list"), "Officer list")

        flush_news_article_related_caches(
            datetime(2021, 9, 3, 9, 0, 0, tzinfo=pytz.utc)
        )

        assert not cache.get(reverse("api:news-articles-list"))
        assert not cache.get(reverse("api:analytics-summary"))
        assert not cache.get(
            reverse("api:officers-timeline", kwargs={"pk": officer_2.id})
        )
        assert not cache.get(
            reverse("api:departments-detail", kwargs={"pk": department_2.agency_slug})
        )
        assert not cache.get(
            reverse(
                "api:departments-news-articles", kwargs={"pk": department_2.agency_slug}
            )
        )
        assert cache.get(reverse("api:officers-timeline", kwargs={"pk": officer_1.id}))
        assert cache.get(
            reverse("api:departments-detail", kwargs={"pk": department_1.agency_slug})
        )
        assert cache.get(
            reverse(
                "api:departments-news-articles", kwargs={"pk": department_1.agency_slug}
            )
        )
        assert cache.get(reverse("api:officers-list"))
