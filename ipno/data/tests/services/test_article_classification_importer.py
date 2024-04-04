from django.test.testcases import TestCase

from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.models import ImportLog
from data.services import ArticleClassificationImporter
from data.tests.services.util import MockDataReconciliation
from news_articles.factories.news_article_classification_factory import (
    NewsArticleClassificationFactory,
)
from news_articles.models import NewsArticleClassification


class ArticleClassificationImporterTestCase(TestCase):
    def setUp(self):
        news_article_classification_1 = NewsArticleClassificationFactory(
            article_id=1,
        )
        news_article_classification_2 = NewsArticleClassificationFactory(
            article_id=2,
        )
        news_article_classification_3 = NewsArticleClassificationFactory(
            article_id=3,
        )
        news_article_classification_4 = NewsArticleClassificationFactory(
            article_id=4,
        )
        news_article_classification_5 = NewsArticleClassificationFactory(
            article_id=5,
        )
        news_article_classification_6 = NewsArticleClassificationFactory(
            article_id=6,
        )

        self.header = list(
            {field.name for field in NewsArticleClassification._meta.fields}
            - NewsArticleClassification.BASE_FIELDS
            - NewsArticleClassification.CUSTOM_FIELDS
        )
        self.news_article_classification1_data = [
            getattr(news_article_classification_1, field) for field in self.header
        ]
        self.news_article_classification2_data = [
            getattr(news_article_classification_2, field) for field in self.header
        ]
        self.news_article_classification3_data = [
            getattr(news_article_classification_3, field) for field in self.header
        ]
        self.news_article_classification4_data = [
            getattr(news_article_classification_4, field) for field in self.header
        ]
        self.news_article_classification5_data = [
            getattr(news_article_classification_5, field) for field in self.header
        ]
        self.news_article_classification6_data = [
            getattr(news_article_classification_6, field) for field in self.header
        ]
        self.news_article_classification5_dup_data = (
            self.news_article_classification5_data.copy()
        )

        NewsArticleClassification.objects.all().delete()

    def test_process_successfully(self):
        NewsArticleClassificationFactory(article_id=1)
        NewsArticleClassificationFactory(article_id=2)
        NewsArticleClassificationFactory(article_id=3)
        NewsArticleClassificationFactory(article_id=6)

        assert NewsArticleClassification.objects.count() == 4

        article_classification_importer = ArticleClassificationImporter("csv_file_path")

        processed_data = {
            "added_rows": [
                self.news_article_classification4_data,
                self.news_article_classification5_data,
                self.news_article_classification5_dup_data,
            ],
            "deleted_rows": [
                self.news_article_classification6_data,
            ],
            "updated_rows": [
                self.news_article_classification1_data,
                self.news_article_classification2_data,
                self.news_article_classification3_data,
            ],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        article_classification_importer.data_reconciliation = MockDataReconciliation(
            processed_data
        )

        result = article_classification_importer.process()

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == article_classification_importer.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert NewsArticleClassification.objects.count() == 5

        assert result

        check_columns = article_classification_importer.column_mappings.copy()

        news_article_classification_data = [
            self.news_article_classification1_data,
            self.news_article_classification2_data,
            self.news_article_classification3_data,
            self.news_article_classification4_data,
            self.news_article_classification5_data,
        ]

        for news_article_classification_item in news_article_classification_data:
            news_article_classification = NewsArticleClassification.objects.filter(
                article_id=news_article_classification_item[check_columns["article_id"]]
            ).first()
            assert news_article_classification
            field_attrs = [
                "text",
                "score",
                "relevant",
                "truth",
            ]

            for attr in field_attrs:
                assert getattr(news_article_classification, attr) == (
                    news_article_classification_item[check_columns[attr]]
                    if news_article_classification_item[check_columns[attr]]
                    else None
                )

    def test_get_article_classification_mappings(self):
        news_article_classification_1 = NewsArticleClassificationFactory()
        news_article_classification_2 = NewsArticleClassificationFactory()

        officer_importer = ArticleClassificationImporter("csv_file_path")
        result = officer_importer.get_article_classification_mappings()

        expected_result = {
            news_article_classification_1.article_id: news_article_classification_1.id,
            news_article_classification_2.article_id: news_article_classification_2.id,
        }

        assert result == expected_result

    def test_delete_not_exist_news_article_classification(self):
        article_classification_importer = ArticleClassificationImporter("csv_file_path")

        processed_data = {
            "added_rows": [],
            "deleted_rows": [
                self.news_article_classification6_data,
            ],
            "updated_rows": [],
            "columns_mapping": {
                column: self.header.index(column) for column in self.header
            },
        }

        article_classification_importer.data_reconciliation = MockDataReconciliation(
            processed_data
        )

        result = article_classification_importer.process()

        assert result

        import_log = ImportLog.objects.order_by("-created_at").last()
        assert import_log.data_model == article_classification_importer.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert not import_log.commit_hash
        assert import_log.created_rows == 0
        assert import_log.updated_rows == 0
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at
