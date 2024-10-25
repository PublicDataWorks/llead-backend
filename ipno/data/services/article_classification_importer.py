from tqdm import tqdm

from data.constants import NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME
from data.services.base_importer import BaseImporter
from data.services.data_reconciliation import DataReconciliation
from news_articles.models import NewsArticle, NewsArticleClassification
from news_articles.services.openai_llm_service import OpenAILLMService


class ArticleClassificationImporter(BaseImporter):  # pragma: no cover
    data_model = NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME

    INT_ATTRIBUTES = [
        "article_id",
    ]

    ATTRIBUTES = list(
        {field.name for field in NewsArticleClassification._meta.fields}
        - NewsArticleClassification.BASE_FIELDS
        - NewsArticleClassification.CUSTOM_FIELDS
        - set(INT_ATTRIBUTES)
    )

    UPDATE_ATTRIBUTES = ATTRIBUTES + INT_ATTRIBUTES + ["news_article_id"]

    def __init__(self, csv_file_path):
        self.new_classifications_attrs = []
        self.update_classifications_attrs = []
        self.new_article_classification_ids = []
        self.delete_classification_ids = []
        self.article_ids = NewsArticle.objects.all().values_list("id", flat=True)
        self.article_classification_mappings = {}

        self.data_reconciliation = DataReconciliation(
            NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME, csv_file_path
        )

        self.openai_service = OpenAILLMService(api_key="your_openai_api_key")

    def handle_record_data(self, row):
        article_classification_data = self.parse_row_data(row, self.column_mappings)

        article_id = article_classification_data["article_id"]
        relation_article_id = article_id if article_id in self.article_ids else None

        article_classification_id = self.article_classification_mappings.get(article_id)
        article_classification_data["news_article_id"] = relation_article_id

        # Call OpenAI LLM service to get confidence score
        article_text = article_classification_data.get("text", "")
        confidence_score = self.openai_service.get_confidence_score(article_text)
        article_classification_data["confidence_score"] = confidence_score

        if article_classification_id:
            article_classification_data["id"] = article_classification_id
            self.update_classifications_attrs.append(article_classification_data)
        elif article_id not in self.new_article_classification_ids:
            self.new_article_classification_ids.append(article_id)
            self.new_classifications_attrs.append(article_classification_data)

    def import_data(self, data):
        self.article_classification_mappings = (
            self.get_article_classification_mappings()
        )

        for row in tqdm(
            data.get("added_rows"), desc="Create new article classifications"
        ):
            self.handle_record_data(row)

        for row in tqdm(
            data.get("deleted_rows"), desc="Delete removed article classifications"
        ):
            article_id = row[self.old_column_mappings["article_id"]]
            article_classification_id = self.article_classification_mappings.get(
                article_id
            )
            if article_classification_id:
                self.delete_classification_ids.append(article_classification_id)

        for row in tqdm(
            data.get("updated_rows"), desc="Update modified article classifications"
        ):
            self.handle_record_data(row)

        return self.bulk_import(
            NewsArticleClassification,
            self.new_classifications_attrs,
            self.update_classifications_attrs,
            self.delete_classification_ids,
        )

    def get_article_classification_mappings(self):
        return {
            article_classification.article_id: article_classification.id
            for article_classification in NewsArticleClassification.objects.only(
                "id", "article_id"
            )
        }
