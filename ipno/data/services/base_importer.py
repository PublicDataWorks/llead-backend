import csv
from io import StringIO
from datetime import datetime
import pytz
import re
import traceback

import requests
from django.conf import settings
from django.utils.text import slugify

from departments.models import Department
from officers.models import Officer
from use_of_forces.models import UseOfForce
from data.models import WrglRepo, ImportLog
from utils.parse_utils import parse_int
from data.constants import (
    WRGL_USER,
    IMPORT_LOG_STATUS_STARTED,
    IMPORT_LOG_STATUS_NO_NEW_COMMIT,
    IMPORT_LOG_STATUS_RUNNING,
    IMPORT_LOG_STATUS_FINISHED,
    IMPORT_LOG_STATUS_ERROR
)


class BaseImporter(object):
    data_model = None
    ATTRIBUTES = []
    NA_ATTRIBUTES = []
    INT_ATTRIBUTES = []
    BATCH_SIZE = 1000

    def format_agency(self, agency):
        agency = re.sub('CSD$', 'PD', agency)
        return re.sub('SO$', 'Sheriff', agency)

    def parse_row_data(self, row):
        row_data = {attr: row[attr] if row[attr] else None for attr in self.ATTRIBUTES if attr in row}

        for attr in self.NA_ATTRIBUTES:
            row_data[attr] = row[attr] if row[attr] != 'NA' else None

        for attr in self.INT_ATTRIBUTES:
            row_data[attr] = parse_int(row[attr]) if row[attr] else None

        return row_data

    def department_mappings(self, agencies):
        slugify_mappings = {slugify(department.name): department.id
                            for department in Department.objects.only('id', 'name')}

        for agency in agencies:
            formatted_agency = self.format_agency(agency)
            slugify_formatted_agency = slugify(formatted_agency)

            if not slugify_mappings.get(slugify_formatted_agency):
                department = Department.objects.create(name=formatted_agency, slug=slugify_formatted_agency)
                slugify_mappings[slugify(department.name)] = department.id

        return slugify_mappings

    def officer_mappings(self):
        return {officer.uid: officer.id for officer in Officer.objects.only('id', 'uid')}

    def uof_mappings(self):
        return {use_of_force.uof_uid: use_of_force.id for use_of_force in UseOfForce.objects.only('id', 'uof_uid')}

    def read_wrgl_csv(self, repo_name, commit_hash):
        url = f'https://www.wrgl.co/api/v1/users/{WRGL_USER}/repos/{repo_name}/commits/{commit_hash}/csv'
        text = requests.get(url).text
        csv_file = csv.DictReader(StringIO(text), delimiter=',')
        return list(csv_file)

    def latest_commit_hash(self, repo_name):
        url = f'https://www.wrgl.co/api/v1/users/{WRGL_USER}/repos/{repo_name}'
        headers = {'Authorization': f'APIKEY {settings.WRGL_API_KEY}'}

        json_data = requests.get(url, headers=headers).json()
        return json_data.get('hash')

    def bulk_import(self, klass, new_items_attrs, update_items_attrs, cleanup_action=None):
        update_item_ids = [attrs['id'] for attrs in update_items_attrs]
        delete_items = klass.objects.exclude(id__in=update_item_ids)

        if cleanup_action:
            cleanup_action(delete_items.values())

        delete_items_count = delete_items.count()
        delete_items.delete()

        for i in range(0, len(new_items_attrs), self.BATCH_SIZE):
            new_objects = [klass(**attrs) for attrs in new_items_attrs[i:i + self.BATCH_SIZE]]
            klass.objects.bulk_create(new_objects)

        for i in range(0, len(update_items_attrs), self.BATCH_SIZE):
            update_objects = [klass(**attrs) for attrs in update_items_attrs[i:i + self.BATCH_SIZE]]
            klass.objects.bulk_update(update_objects, self.UPDATE_ATTRIBUTES)

        return {
            'created_rows': len(new_items_attrs),
            'updated_rows': len(update_items_attrs),
            'deleted_rows': delete_items_count,
        }

    def import_data(self, data):
        raise NotImplementedError

    def update_import_log(self, import_log, log_data):
        for (key, value) in log_data.items():
            setattr(import_log, key, value)
        import_log.save()

    def process(self):
        import_log = ImportLog.objects.create(
            data_model=self.data_model,
            status=IMPORT_LOG_STATUS_STARTED,
            started_at=datetime.now(pytz.utc)
        )
        wrgl_repo = WrglRepo.objects.filter(data_model=self.data_model).first()

        if wrgl_repo:
            self.update_import_log(
                import_log,
                {
                    'repo_name': wrgl_repo.repo_name,
                }
            )

            commit_hash = self.latest_commit_hash(wrgl_repo.repo_name)
            if commit_hash:
                if wrgl_repo.commit_hash != commit_hash:
                    self.update_import_log(
                        import_log,
                        {
                            'commit_hash': commit_hash,
                            'status': IMPORT_LOG_STATUS_RUNNING,
                        }
                    )
                    try:
                        data = self.read_wrgl_csv(wrgl_repo.repo_name, commit_hash)
                        import_results = self.import_data(data)
                        wrgl_repo.commit_hash = commit_hash
                        wrgl_repo.save()
                        self.update_import_log(
                            import_log,
                            {
                                'status': IMPORT_LOG_STATUS_FINISHED,
                                'finished_at': datetime.now(pytz.utc),
                                'created_rows': import_results.get('created_rows'),
                                'updated_rows': import_results.get('updated_rows'),
                                'deleted_rows': import_results.get('deleted_rows')
                            }
                        )
                        return True
                    except Exception:
                        self.update_import_log(
                            import_log,
                            {
                                'status': IMPORT_LOG_STATUS_ERROR,
                                'finished_at': datetime.now(pytz.utc),
                                'error_message': f'Error occurs while importing data!\n{traceback.format_exc()}',
                            }
                        )
                else:
                    self.update_import_log(
                        import_log,
                        {
                            'commit_hash': commit_hash,
                            'status': IMPORT_LOG_STATUS_NO_NEW_COMMIT,
                            'finished_at': datetime.now(pytz.utc),
                        }
                    )
            else:
                self.update_import_log(
                    import_log,
                    {
                        'status': IMPORT_LOG_STATUS_ERROR,
                        'finished_at': datetime.now(pytz.utc),
                        'error_message': f'Cannot get latest commit hash from Wrgl for repo {wrgl_repo.repo_name}!'
                    }
                )

        else:
            self.update_import_log(
                import_log,
                {
                    'status': IMPORT_LOG_STATUS_ERROR,
                    'finished_at': datetime.now(pytz.utc),
                    'error_message': 'Cannot find Wrgl Repo!',
                }
            )
