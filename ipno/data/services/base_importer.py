import csv
import json
from io import StringIO
import urllib
from datetime import datetime
import pytz
import re

from django.conf import settings

from departments.models import Department
from officers.models import Officer
from use_of_forces.models import UseOfForce
from data.models import WrglRepo, ImportLog
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

    def format_agency(self, agency):
        agency = re.sub('CSD$', 'PD', agency)
        return re.sub('SO$', 'Sheriff', agency)

    def get_or_create_department(self, agency):
        agency = re.sub('CSD$', 'PD', agency)
        agency = re.sub('SO$', 'Sheriff', agency)
        department, _ = Department.objects.get_or_create(name=agency)
        return department

    def department_mappings(self, agencies):
        mappings = {department.name: department.id for department in Department.objects.only('id', 'name')}
        for agency in agencies:
            formatted_agency = self.format_agency(agency)
            if not mappings.get(formatted_agency):
                department = Department.objects.create(name=formatted_agency)
                mappings[department.name] = department.id
        return mappings

    def officer_mappings(self):
        return {officer.uid: officer.id for officer in Officer.objects.only('id', 'uid')}

    def uof_mappings(self):
        return {use_of_force.uof_uid: use_of_force.id for use_of_force in UseOfForce.objects.only('id', 'uof_uid')}

    def read_wrgl_csv(self, repo_name, commit_hash):
        url = f'https://www.wrgl.co/api/v1/users/{WRGL_USER}/repos/{repo_name}/commits/{commit_hash}/csv'
        ftp_stream = urllib.request.urlopen(url)
        text = ftp_stream.read().decode('utf-8')
        csv_file = csv.DictReader(StringIO(text), delimiter=',')
        return list(csv_file)

    def latest_commit_hash(self, repo_name):
        url = f'https://www.wrgl.co/api/v1/users/{WRGL_USER}/repos/{repo_name}'
        request = urllib.request.Request(url)
        request.add_header('Authorization', f'APIKEY {settings.WRGL_API_KEY}')

        ftp_stream = urllib.request.urlopen(request)
        json_data = json.loads(ftp_stream.read().decode('utf-8'))
        return json_data.get('hash')

    def wrgl_repo(self):
        return WrglRepo.objects.filter(data_model=self.data_model).first()

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
                    except Exception:
                        self.update_import_log(
                            import_log,
                            {
                                'status': IMPORT_LOG_STATUS_ERROR,
                                'finished_at': datetime.now(pytz.utc),
                                'error_message': 'Error occurs while importing data!',
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
