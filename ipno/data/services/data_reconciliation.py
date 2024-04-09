import pandas as pd

from appeals.models.appeal import Appeal
from brady.models import Brady
from citizens.models.citizen import Citizen
from complaints.models.complaint import Complaint
from data.constants import (
    AGENCY_MODEL_NAME,
    APPEAL_MODEL_NAME,
    BRADY_MODEL_NAME,
    CITIZEN_MODEL_NAME,
    COMPLAINT_MODEL_NAME,
    DOCUMENT_MODEL_NAME,
    EVENT_MODEL_NAME,
    NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME,
    OFFICER_MODEL_NAME,
    PERSON_MODEL_NAME,
    POST_OFFICE_HISTORY_MODEL_NAME,
    USE_OF_FORCE_MODEL_NAME,
)
from departments.models.department import Department
from documents.models.document import Document
from news_articles.models.news_article_classification import NewsArticleClassification
from officers.models.event import Event
from officers.models.officer import Officer
from people.models.person import Person
from post_officer_history.models.post_officer_history import PostOfficerHistory
from use_of_forces.models.use_of_force import UseOfForce


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
        if model_name == USE_OF_FORCE_MODEL_NAME:
            return UseOfForce
        if model_name == CITIZEN_MODEL_NAME:
            return Citizen
        if model_name == APPEAL_MODEL_NAME:
            return Appeal
        if model_name == EVENT_MODEL_NAME:
            return Event
        if model_name == POST_OFFICE_HISTORY_MODEL_NAME:
            return PostOfficerHistory
        if model_name == PERSON_MODEL_NAME:
            return Person
        if model_name == DOCUMENT_MODEL_NAME:
            return Document
        raise ValueError(f"Data reconciliation does not support model: {model_name}")

    def _get_index_colums(self):
        if self.model_name == BRADY_MODEL_NAME:
            return ["brady_uid"]
        if self.model_name == AGENCY_MODEL_NAME:
            return ["agency_slug"]
        if self.model_name == OFFICER_MODEL_NAME:
            return ["uid"]
        if self.model_name == NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME:
            return ["article_id"]
        if self.model_name == COMPLAINT_MODEL_NAME:
            return ["allegation_uid"]
        if self.model_name == USE_OF_FORCE_MODEL_NAME:
            return ["uof_uid"]
        if self.model_name == CITIZEN_MODEL_NAME:
            return ["citizen_uid"]
        if self.model_name == APPEAL_MODEL_NAME:
            return ["appeal_uid"]
        if self.model_name == EVENT_MODEL_NAME:
            return ["event_uid"]
        if self.model_name == POST_OFFICE_HISTORY_MODEL_NAME:
            return ["uid"]
        if self.model_name == PERSON_MODEL_NAME:
            return ["person_id"]
        if self.model_name == DOCUMENT_MODEL_NAME:
            return ["docid", "hrg_no", "matched_uid", "agency"]
        raise ValueError(
            f"Data reconciliation does not support model: {self.model_name}"
        )

    def _get_columns(self):
        columns = [
            field.name
            for field in self.model_class._meta.fields
            if field.name not in self.model_class.BASE_FIELDS
            and field.name not in self.model_class.CUSTOM_FIELDS
        ]

        if self.model_name == DOCUMENT_MODEL_NAME:
            columns += ["page_count"]

        return columns

    def _get_queryset(self):
        return self.model_class.objects.all().values()

    def _filter_by_idx_columns(self, df, source_df, idx_columns):
        filters = []
        for column in idx_columns:
            filters.append(df[column].isin(source_df[column].tolist()))
        combined_fileter = filters[0]
        for filter in filters[1:]:
            combined_fileter &= filter

        return df[combined_fileter]

    def reconcile_data(self):
        columns = self._get_columns()
        idx_columns = self._get_index_colums()

        df_csv = pd.read_csv(
            self.csv_file_path, usecols=columns, dtype="string", keep_default_na=False
        ).fillna("")[columns]

        queryset = self._get_queryset()
        df_db = pd.DataFrame(list(queryset), columns=columns, dtype="string").fillna(
            ""
        )[columns]

        df_all = pd.merge(df_db, df_csv, how="outer", indicator=True, on=idx_columns)
        df_all.iloc[:, :-1].fillna("", inplace=True)

        added = df_all[df_all["_merge"] == "right_only"]
        added_rows = (
            self._filter_by_idx_columns(df_csv, added, idx_columns).to_numpy().tolist()
        )

        deleted = df_all[df_all["_merge"] == "left_only"]
        deleted_rows = (
            self._filter_by_idx_columns(df_db, deleted, idx_columns).to_numpy().tolist()
        )

        # Create a boolean mask to identify rows where "_merge" is "both"
        merge_mask = df_all["_merge"] == "both"

        # Create a list to store the boolean masks for each column comparison
        diff_masks = []

        # Iterate over the columns and create boolean masks for each comparison
        for col in columns:
            if col in idx_columns:
                continue
            col_x = col + "_x"
            col_y = col + "_y"
            diff_mask = (df_all[col_x] != df_all[col_y]) & merge_mask
            diff_masks.append(diff_mask)

        # Combine the boolean masks using logical OR
        combined_mask = diff_masks[0]
        for mask in diff_masks[1:]:
            combined_mask |= mask

        # Select the rows that satisfy the combined mask
        df_diff = df_all[combined_mask]
        updated_rows = (
            self._filter_by_idx_columns(df_csv, df_diff, idx_columns)
            .to_numpy()
            .tolist()
        )

        # Reconcile the data
        return {
            "added_rows": added_rows,
            "deleted_rows": deleted_rows,
            "updated_rows": updated_rows,
            "columns_mapping": {column: columns.index(column) for column in columns},
        }
