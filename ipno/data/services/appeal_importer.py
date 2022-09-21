from itertools import chain

from tqdm import tqdm

from appeals.models import Appeal
from data.services import BaseImporter
from data.constants import APPEAL_MODEL_NAME


class AppealImporter(BaseImporter):
    data_model = APPEAL_MODEL_NAME
    ATTRIBUTES = [
        'appeal_uid',
        'docket_no',
        'counsel',
        'charging_supervisor',
        'appeal_disposition',
        'action_appealed',
        'appealed',
        'motions',
    ]

    UPDATE_ATTRIBUTES = ATTRIBUTES + ['officer_id', 'department_id']

    def __init__(self):
        self.new_appeals_attrs = []
        self.update_appeals_attrs = []
        self.new_appeal_uids = []
        self.delete_appeals_ids = []
        self.officer_mappings = {}
        self.department_mappings = {}
        self.appeal_mappings = {}

    def handle_record_data(self, row):
        agency = row[self.column_mappings['agency']]
        officer_uid = row[self.column_mappings['uid']]
        appeal_data = self.parse_row_data(row, self.column_mappings)

        appeal_uid = appeal_data['appeal_uid']

        department_id = self.department_mappings.get(agency)
        appeal_data['department_id'] = department_id

        officer_id = self.officer_mappings.get(officer_uid)
        appeal_data['officer_id'] = officer_id

        appeal_id = self.appeal_mappings.get(appeal_uid)

        if appeal_id:
            appeal_data['id'] = appeal_id
            self.update_appeals_attrs.append(appeal_data)
        elif appeal_uid not in self.new_appeal_uids:
            self.new_appeal_uids.append(appeal_uid)
            self.new_appeals_attrs.append(appeal_data)

    def import_data(self, data):
        saved_data = list(chain(
            data.get('added_rows', []),
            data.get('updated_rows', []),
        ))
        deleted_data = data.get('deleted_rows', [])

        self.officer_mappings = self.get_officer_mappings()
        agencies = {row[self.column_mappings['agency']] for row in saved_data if row[self.column_mappings['agency']]}
        agencies.update([
            row[self.old_column_mappings['agency']] for row in deleted_data if row[self.old_column_mappings['agency']]
        ])
        self.department_mappings = self.get_department_mappings(agencies)

        self.appeal_mappings = self.get_appeal_mappings()

        for row in tqdm(data.get('added_rows'), desc='Create new appeals'):
            self.handle_record_data(row)

        for row in tqdm(data.get('deleted_rows'), desc='Delete removed appeals'):
            appeal_uid = row[self.old_column_mappings['appeal_uid']]
            appeal_id = self.appeal_mappings.get(appeal_uid)
            if appeal_id:
                self.delete_appeals_ids.append(appeal_id)

        for row in tqdm(data.get('updated_rows'), desc='Update modified appeals'):
            self.handle_record_data(row)

        return self.bulk_import(Appeal, self.new_appeals_attrs, self.update_appeals_attrs, self.delete_appeals_ids)
