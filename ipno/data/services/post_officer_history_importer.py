from tqdm import tqdm

from data.constants import POST_OFFICE_HISTORY_MODEL_NAME
from data.services.base_importer import BaseImporter
from post_officer_history.models import PostOfficerHistory


class PostOfficerHistoryImporter(BaseImporter):  # pragma: no cover
    data_model = POST_OFFICE_HISTORY_MODEL_NAME

    DATE_ATTRIBUTES = ["hire_date"]

    ATTRIBUTES = list(
        {field.name for field in PostOfficerHistory._meta.fields}
        - PostOfficerHistory.BASE_FIELDS
        - PostOfficerHistory.CUSTOM_FIELDS
        - set(DATE_ATTRIBUTES)
    )

    UPDATE_ATTRIBUTES = ATTRIBUTES + DATE_ATTRIBUTES + ["officer_id", "department_id"]

    def __init__(self):
        self.new_post_officer_history_attrs = []
        self.update_post_officer_history_attrs = []
        self.new_uids = []
        self.delete_post_officer_history_ids = []
        self.officer_mappings = {}
        self.department_mappings = {}
        self.post_officer_history_mappings = {}

    def handle_record_data(self, row):
        uid = row[self.column_mappings["uid"]]
        officer_id = self.officer_mappings[uid]

        agency = row[self.column_mappings["agency"]]
        department_id = self.department_mappings[agency]

        post_officer_history_data = self.parse_row_data(row, self.column_mappings)

        post_officer_history_id = self.post_officer_history_mappings.get(uid)
        post_officer_history_data["officer_id"] = officer_id
        post_officer_history_data["department_id"] = department_id

        if post_officer_history_id:
            post_officer_history_data["id"] = post_officer_history_id
            self.update_post_officer_history_attrs.append(post_officer_history_data)
        elif uid not in self.new_uids:
            self.new_uids.append(uid)
            self.new_post_officer_history_attrs.append(post_officer_history_data)

    def import_data(self, data):
        self.post_officer_history_mappings = self.get_post_officer_history_mappings()
        self.officer_mappings = self.get_officer_mappings()
        self.department_mappings = self.get_department_mappings()

        for row in tqdm(data.get("added_rows"), desc="Create new post officer history"):
            self.handle_record_data(row)

        for row in tqdm(
            data.get("deleted_rows"), desc="Delete removed post officer history"
        ):
            uid = row[self.old_column_mappings["uid"]]
            post_officer_history_id = self.post_officer_history_mappings.get(uid)
            if post_officer_history_id:
                self.delete_post_officer_history_ids.append(post_officer_history_id)

        for row in tqdm(
            data.get("updated_rows"), desc="Update modified post officer history"
        ):
            self.handle_record_data(row)

        return self.bulk_import(
            PostOfficerHistory,
            self.new_post_officer_history_attrs,
            self.update_post_officer_history_attrs,
            self.delete_post_officer_history_ids,
        )

    def get_post_officer_history_mappings(self):
        return {
            post_officer_history.uid: post_officer_history.id
            for post_officer_history in PostOfficerHistory.objects.only("id", "uid")
        }
