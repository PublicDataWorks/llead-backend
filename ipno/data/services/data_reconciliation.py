import pandas as pd

from brady.models import Brady
from complaints.models.complaint import Complaint
from data.constants import (
    AGENCY_MODEL_NAME,
    BRADY_MODEL_NAME,
    COMPLAINT_MODEL_NAME,
    NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME,
    OFFICER_MODEL_NAME,
)
from departments.models.department import Department
from news_articles.models.news_article_classification import NewsArticleClassification
from officers.models.officer import Officer


class DataReconciliation:
    def __init__(self, model_name, csv_file_path):
        self.model_name = model_name
        self.model_class = self._get_model_class(model_name)
        self.csv_file_path = csv_file_path

    def _get_model_class(self, model_name):
        if model_name == BRADY_MODEL_NAME:
            return Brady
        if model_name == AGENCY_MODEL_NAME:
            return Department
        if model_name == OFFICER_MODEL_NAME:
            return Officer
        if model_name == NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME:
            return NewsArticleClassification
        if model_name == COMPLAINT_MODEL_NAME:
            return Complaint
        raise ValueError(f"Data reconciliation does not support model: {model_name}")

    def _get_index_colum(self):
        if self.model_name == BRADY_MODEL_NAME:
            return "brady_uid"
        if self.model_name == AGENCY_MODEL_NAME:
            return "agency_slug"
        if self.model_name == OFFICER_MODEL_NAME:
            return "uid"
        if self.model_name == NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME:
            return "article_id"
        if self.model_name == COMPLAINT_MODEL_NAME:
            return "allegation_uid"
        raise ValueError(
            f"Data reconciliation does not support model: {self.model_name}"
        )

    def _get_columns(self):
        return [
            field.name
            for field in self.model_class._meta.fields
            if field.name not in self.model_class.BASE_FIELDS
            and field.name not in self.model_class.CUSTOM_FIELDS
        ]

    def _get_queryset(self):
        return self.model_class.objects.all().values()

    def reconcile_data(self):
        columns = self._get_columns()
        idx_column = self._get_index_colum()

        df_csv = pd.read_csv(
            self.csv_file_path, usecols=columns, dtype="string", keep_default_na=False
        ).fillna("")

        queryset = self._get_queryset()
        df_db = pd.DataFrame(list(queryset), columns=columns, dtype="string").fillna("")

        df_all = pd.merge(df_db, df_csv, how="outer", indicator=True, on=idx_column)
        df_all.iloc[:, :-1].fillna("", inplace=True)

        added = df_all[df_all["_merge"] == "right_only"]
        added_rows = (
            df_csv[df_csv[idx_column].isin(added[idx_column].tolist())]
            .to_numpy()
            .tolist()
        )

        deleted = df_all[df_all["_merge"] == "left_only"]
        deleted_rows = (
            df_db[df_db[idx_column].isin(deleted[idx_column].tolist())]
            .to_numpy()
            .tolist()
        )

        # Create a boolean mask to identify rows where "_merge" is "both"
        merge_mask = df_all["_merge"] == "both"

        # Create a list to store the boolean masks for each column comparison
        diff_masks = []

        # Iterate over the columns and create boolean masks for each comparison
        for i in range(1, len(columns)):
            col_x = columns[i] + "_x"
            col_y = columns[i] + "_y"
            diff_mask = (df_all[col_x] != df_all[col_y]) & merge_mask
            diff_masks.append(diff_mask)

        # Combine the boolean masks using logical OR
        combined_mask = diff_masks[0]
        for mask in diff_masks[1:]:
            combined_mask |= mask

        # Select the rows that satisfy the combined mask
        df_diff = df_all[combined_mask]
        updated_rows = (
            df_csv[df_csv[idx_column].isin(df_diff[idx_column].tolist())]
            .to_numpy()
            .tolist()
        )

        # Reconcile the data
        return {
            "added_rows": added_rows,
            "deleted_rows": deleted_rows,
            "updated_rows": updated_rows,
        }
