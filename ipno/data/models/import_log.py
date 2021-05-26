from django.db import models

from utils.models import TimeStampsModel
from data.constants import IMPORT_LOG_STATUSES


class ImportLog(TimeStampsModel):
    data_model = models.CharField(max_length=255)
    repo_name = models.CharField(max_length=255, null=True)
    commit_hash = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=32, choices=IMPORT_LOG_STATUSES)
    created_rows = models.IntegerField(null=True)
    updated_rows = models.IntegerField(null=True)
    deleted_rows = models.IntegerField(null=True)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    error_message = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.repo_name}-{self.data_model} {self.commit_hash}'
