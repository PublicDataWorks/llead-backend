import datetime
from urllib.parse import urlencode

from django.urls import reverse

from rest_framework import status

from freezegun import freeze_time

from authentication.models import User
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from historical_data.constants import (
    RECENT_DEPARTMENT_TYPE,
    RECENT_DOCUMENT_TYPE,
    RECENT_NEWS_ARTICLE_TYPE,
    RECENT_OFFICER_TYPE,
)
from historical_data.factories import AnonymousItemFactory, AnonymousQueryFactory
from historical_data.models import AnonymousItem, AnonymousQuery
from news_articles.factories import NewsArticleFactory, NewsArticleSourceFactory
from officers.factories import EventFactory, OfficerFactory
from people.factories import PersonFactory
from test_utils.auth_api_test_case import AuthAPITestCase


class HistoricalDataViewSetTestCase(AuthAPITestCase):
    def test_recent_items(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(
            first_name="David", last_name="Jonesworth", department=department_2
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )
        EventFactory(
            department=department_2,
            officer=officer,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department_2,
            officer=officer,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 8).date(),
            source=source,
            is_hidden=True,
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_2.slug},
            {
                "type": RECENT_DEPARTMENT_TYPE,
                "id": "falsy-slug",
            },
            {
                "type": RECENT_OFFICER_TYPE,
                "id": "-1",
            },
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        response = self.auth_client.get(reverse("api:historical-data-recent-items"))

        expected_data = [
            {
                "id": document.id,
                "document_type": document.document_type,
                "title": document.title,
                "url": document.url,
                "preview_image_url": document.preview_image_url,
                "incident_date": str(document.incident_date),
                "pages_count": document.pages_count,
                "departments": [
                    {
                        "id": department_1.slug,
                        "name": department_1.name,
                    }
                ],
                "type": RECENT_DOCUMENT_TYPE,
            },
            {
                "id": department_1.slug,
                "name": department_1.name,
                "city": department_1.city,
                "parish": department_1.parish,
                "location_map_url": department_1.location_map_url,
                "type": RECENT_DEPARTMENT_TYPE,
            },
            {
                "id": officer.id,
                "name": "David Jonesworth",
                "badges": ["12435"],
                "departments": [
                    {
                        "id": department_2.slug,
                        "name": department_2.name,
                    }
                ],
                "latest_rank": "senior",
                "type": RECENT_OFFICER_TYPE,
            },
            {
                "id": department_2.slug,
                "name": department_2.name,
                "city": department_2.city,
                "parish": department_2.parish,
                "location_map_url": department_2.location_map_url,
                "type": RECENT_DEPARTMENT_TYPE,
            },
            {
                "id": news_article.id,
                "source_name": source.source_display_name,
                "title": news_article.title,
                "url": news_article.url,
                "date": "2021-09-07",
                "type": "NEWS_ARTICLE",
                "author": news_article.author,
            },
        ]

        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data

    def test_no_recent_items(self):
        response = self.auth_client.get(reverse("api:historical-data-recent-items"))
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == []

    def test_update_new_recent_items(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        old_recent_item = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
        ]

        self.user.recent_items = old_recent_item
        self.user.save()

        data = {"type": RECENT_DEPARTMENT_TYPE, "id": department_2.slug}

        response = self.auth_client.post(
            reverse("api:historical-data-recent-items"), data, format="json"
        )

        expected_data = {"detail": "updated user recent items"}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [data, *old_recent_item]

    def test_update_existed_recent_items(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        old_recent_item = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
        ]

        self.user.recent_items = old_recent_item
        self.user.save()

        data = {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug}

        response = self.auth_client.post(
            reverse("api:historical-data-recent-items"), data, format="json"
        )

        expected_data = {"detail": "updated user recent items"}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
        ]

    def test_recent_queries(self):
        self.user.recent_queries = ["query 2", "query 1"]
        self.user.save()

        response = self.auth_client.get(reverse("api:historical-data-recent-queries"))
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == ["query 2", "query 1"]

    def test_no_recent_queries(self):
        response = self.auth_client.get(reverse("api:historical-data-recent-queries"))
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert not result

    def test_update_new_recent_queries(self):
        self.user.recent_queries = ["query 2", "query 1"]
        self.user.save()

        data = {"q": "query 3"}

        response = self.auth_client.post(
            reverse("api:historical-data-recent-queries"), data, format="json"
        )

        expected_data = {"detail": "updated user recent queries"}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_queries == [data.get("q"), "query 2", "query 1"]

    def test_update_existed_recent_queries(self):
        self.user.recent_queries = ["query 2", "query 1"]
        self.user.save()

        data = {"q": "query 1"}

        response = self.auth_client.post(
            reverse("api:historical-data-recent-queries"), data, format="json"
        )

        expected_data = {"detail": "updated user recent queries"}

        result = response.data

        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_queries == ["query 1", "query 2"]

    def test_delete_recent_officer_successfully(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"type": RECENT_OFFICER_TYPE, "id": officer.id}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = {"detail": "deleted user recent item"}

        result = response.data
        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]

    def test_delete_recent_department_successfully(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = {"detail": "deleted user recent item"}

        result = response.data
        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]

    def test_delete_recent_document_successfully(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"type": RECENT_DOCUMENT_TYPE, "id": document.id}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = {"detail": "deleted user recent item"}

        result = response.data
        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]

    def test_delete_recent_news_article_successfully(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {
            "type": RECENT_NEWS_ARTICLE_TYPE,
            "id": news_article.id,
        }

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = {"detail": "deleted user recent item"}

        result = response.data
        user = User.objects.first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert user.recent_items == [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
        ]

    def test_not_delete_non_existed_item(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"type": RECENT_DEPARTMENT_TYPE, "id": department_2.slug}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = None

        result = response.data

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert result == expected_data

    def test_delete_without_item_type(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"id": department.slug}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = {"error": "id and type is required"}

        result = response.data

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == expected_data

    def test_delete_without_item_id(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"type": RECENT_DEPARTMENT_TYPE}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = {"error": "id and type is required"}

        result = response.data

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert result == expected_data

    def test_not_delete_department_with_digit_item_id(self):
        department = DepartmentFactory(name="Baton Rouge PD")
        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        document = DocumentFactory()
        document.departments.add(department)

        self.user.recent_items = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
            {
                "type": RECENT_NEWS_ARTICLE_TYPE,
                "id": news_article.id,
            },
        ]
        self.user.save()

        data = {"type": RECENT_DEPARTMENT_TYPE, "id": "1"}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.auth_client.delete(f"{delete_url}?{params}")

        expected_data = None

        result = response.data

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert result == expected_data

    def test_recent_items_of_anonymous_user(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(
            first_name="David", last_name="Jonesworth", department=department_2
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )
        EventFactory(
            department=department_2,
            officer=officer,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department_2,
            officer=officer,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 8).date(),
            source=source,
            is_hidden=True,
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        with freeze_time("2021-09-03 8:00:00"):
            AnonymousItemFactory(
                item_id=document.id,
                item_type=RECENT_DOCUMENT_TYPE,
            )
        with freeze_time("2021-09-02 9:00:00"):
            AnonymousItemFactory(
                item_id=department_1.slug,
                item_type=RECENT_DEPARTMENT_TYPE,
            )
        with freeze_time("2021-09-01 9:00:00"):
            AnonymousItemFactory(
                item_id=officer.id,
                item_type=RECENT_OFFICER_TYPE,
            )
        with freeze_time("2021-09-06 11:00:00"):
            AnonymousItemFactory(
                item_id=department_2.slug,
                item_type=RECENT_DEPARTMENT_TYPE,
            )
        with freeze_time("2021-09-05 8:00:00"):
            AnonymousItemFactory(
                item_id="falsy-slug",
                item_type=RECENT_DEPARTMENT_TYPE,
            )
        with freeze_time("2021-09-04 8:00:00"):
            AnonymousItemFactory(
                item_id="-1",
                item_type=RECENT_OFFICER_TYPE,
            )
        with freeze_time("2021-09-03 10:00:00"):
            AnonymousItemFactory(
                item_id=news_article.id,
                item_type=RECENT_NEWS_ARTICLE_TYPE,
            )

        response = self.client.get(reverse("api:historical-data-recent-items"))

        expected_data = [
            {
                "id": department_2.slug,
                "name": department_2.name,
                "city": department_2.city,
                "parish": department_2.parish,
                "location_map_url": department_2.location_map_url,
                "type": RECENT_DEPARTMENT_TYPE,
            },
            {
                "id": news_article.id,
                "source_name": source.source_display_name,
                "title": news_article.title,
                "url": news_article.url,
                "date": "2021-09-07",
                "type": "NEWS_ARTICLE",
                "author": news_article.author,
            },
            {
                "id": document.id,
                "document_type": document.document_type,
                "title": document.title,
                "url": document.url,
                "preview_image_url": document.preview_image_url,
                "incident_date": str(document.incident_date),
                "pages_count": document.pages_count,
                "departments": [
                    {
                        "id": department_1.slug,
                        "name": department_1.name,
                    }
                ],
                "type": RECENT_DOCUMENT_TYPE,
            },
            {
                "id": department_1.slug,
                "name": department_1.name,
                "city": department_1.city,
                "parish": department_1.parish,
                "location_map_url": department_1.location_map_url,
                "type": RECENT_DEPARTMENT_TYPE,
            },
            {
                "id": officer.id,
                "name": "David Jonesworth",
                "badges": ["12435"],
                "departments": [
                    {
                        "id": department_2.slug,
                        "name": department_2.name,
                    }
                ],
                "latest_rank": "senior",
                "type": RECENT_OFFICER_TYPE,
            },
        ]

        result = response.data
        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data

    def test_update_anonymous_user_recent_items_existed(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        old_recent_item = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
        ]

        for index, item in enumerate(old_recent_item):
            with freeze_time(f"2021-09-03 {8+index}:00:00"):
                AnonymousItemFactory(
                    item_id=item["id"],
                    item_type=item["type"],
                )

        current_latest_item = AnonymousItem.objects.order_by("-last_visited").first()

        new_item = {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug}

        assert current_latest_item.item_id == str(old_recent_item[2]["id"])
        assert current_latest_item.item_type == old_recent_item[2]["type"]

        response = self.client.post(
            reverse("api:historical-data-recent-items"), new_item, format="json"
        )
        expected_data = {"detail": "updated anonymous user recent items"}

        result = response.data
        latest_item = AnonymousItem.objects.order_by("-last_visited").first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert latest_item.item_id == new_item["id"]
        assert latest_item.item_type == new_item["type"]

    def test_update_anonymous_user_recent_items_not_existed(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(first_name="David", last_name="Jonesworth")
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        old_recent_item = [
            {"type": RECENT_DOCUMENT_TYPE, "id": document.id},
            {"type": RECENT_DEPARTMENT_TYPE, "id": department_1.slug},
            {"type": RECENT_OFFICER_TYPE, "id": officer.id},
        ]

        for index, item in enumerate(old_recent_item):
            with freeze_time(f"2021-09-03 {8+index}:00:00"):
                AnonymousItemFactory(
                    item_id=item["id"],
                    item_type=item["type"],
                )

        new_item = {"type": RECENT_DEPARTMENT_TYPE, "id": department_2.slug}

        response = self.client.post(
            reverse("api:historical-data-recent-items"), new_item, format="json"
        )
        expected_data = {"detail": "updated anonymous user recent items"}

        result = response.data
        latest_item = AnonymousItem.objects.order_by("-last_visited").first()

        assert response.status_code == status.HTTP_200_OK
        assert result == expected_data
        assert latest_item.item_id == new_item["id"]
        assert latest_item.item_type == new_item["type"]

    def test_not_delete_if_anonymous_user(self):
        department_1 = DepartmentFactory(name="Baton Rouge PD")
        department_2 = DepartmentFactory(name="New Orleans PD")

        officer = OfficerFactory(
            first_name="David", last_name="Jonesworth", department=department_2
        )
        person = PersonFactory(canonical_officer=officer)
        person.officers.add(officer)
        person.save()
        EventFactory(
            officer=officer,
            department=department_2,
            badge_no="12435",
        )
        EventFactory(
            department=department_2,
            officer=officer,
            rank_desc="junior",
            year=2018,
            month=4,
            day=5,
        )
        EventFactory(
            department=department_2,
            officer=officer,
            rank_desc="senior",
            year=2020,
            month=4,
            day=5,
        )

        source = NewsArticleSourceFactory(source_display_name="dummy")
        news_article = NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 7).date(), source=source
        )

        NewsArticleFactory(
            published_date=datetime.datetime(2021, 9, 8).date(),
            source=source,
            is_hidden=True,
        )

        document = DocumentFactory()
        document.departments.add(department_1)

        DepartmentFactory()
        OfficerFactory()
        DocumentFactory()

        with freeze_time("2021-09-03 8:00:00"):
            AnonymousItemFactory(
                item_id=document.id,
                item_type=RECENT_DOCUMENT_TYPE,
            )
        with freeze_time("2021-09-02 9:00:00"):
            AnonymousItemFactory(
                item_id=department_1.slug,
                item_type=RECENT_DEPARTMENT_TYPE,
            )
        with freeze_time("2021-09-01 9:00:00"):
            AnonymousItemFactory(
                item_id=officer.id,
                item_type=RECENT_OFFICER_TYPE,
            )
        with freeze_time("2021-09-06 11:00:00"):
            AnonymousItemFactory(
                item_id=department_2.slug,
                item_type=RECENT_DEPARTMENT_TYPE,
            )
        with freeze_time("2021-09-05 8:00:00"):
            AnonymousItemFactory(
                item_id="falsy-slug",
                item_type=RECENT_DEPARTMENT_TYPE,
            )
        with freeze_time("2021-09-04 8:00:00"):
            AnonymousItemFactory(
                item_id="-1",
                item_type=RECENT_OFFICER_TYPE,
            )
        with freeze_time("2021-09-03 10:00:00"):
            AnonymousItemFactory(
                item_id=news_article.id,
                item_type=RECENT_NEWS_ARTICLE_TYPE,
            )

        data = {"type": RECENT_DOCUMENT_TYPE, "id": document.id}

        delete_url = reverse("api:historical-data-recent-items")
        params = urlencode(data)

        response = self.client.delete(f"{delete_url}?{params}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_recent_queries_of_anonymous_user(self):
        with freeze_time("2021-09-03 8:00:00"):
            AnonymousQueryFactory(query="query 1")
        with freeze_time("2021-09-03 9:00:00"):
            AnonymousQueryFactory(query="query 2")
        with freeze_time("2021-09-03 9:00:00"):
            AnonymousQueryFactory(query="query 3")

        response = self.client.get(reverse("api:historical-data-recent-queries"))
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert result == ["query 3", "query 2", "query 1"]

    def test_no_recent_queries_of_anonymous_user(self):
        response = self.client.get(reverse("api:historical-data-recent-queries"))
        result = response.data

        assert response.status_code == status.HTTP_200_OK
        assert not result

    def test_update_recent_queries_existed_of_anonymous_user(self):
        with freeze_time("2021-09-03 8:00:00"):
            AnonymousQueryFactory(query="query 1")
        with freeze_time("2021-09-03 9:00:00"):
            AnonymousQueryFactory(query="query 2")
        with freeze_time("2021-09-03 9:00:00"):
            AnonymousQueryFactory(query="query 3")

        data = {"q": "query 2"}

        latest_query = AnonymousQuery.objects.order_by("-last_visited").first()
        assert latest_query.query == "query 3"

        response = self.client.post(
            reverse("api:historical-data-recent-queries"), data, format="json"
        )

        latest_query = AnonymousQuery.objects.order_by("-last_visited").first()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "updated anonymous user recent queries"}
        assert latest_query.query == "query 2"

    def test_update_recent_queries_not_existed_of_anonymous_user(self):
        with freeze_time("2021-09-03 8:00:00"):
            AnonymousQueryFactory(query="query 1")
        with freeze_time("2021-09-03 9:00:00"):
            AnonymousQueryFactory(query="query 2")
        with freeze_time("2021-09-03 9:00:00"):
            AnonymousQueryFactory(query="query 3")

        data = {"q": "query 4"}

        latest_query = AnonymousQuery.objects.order_by("-last_visited").first()
        assert latest_query.query == "query 3"

        response = self.client.post(
            reverse("api:historical-data-recent-queries"), data, format="json"
        )

        latest_query = AnonymousQuery.objects.order_by("-last_visited").first()

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "updated anonymous user recent queries"}
        assert latest_query.query == "query 4"
