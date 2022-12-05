from django.db import models

from data.constants import IMPORT_LOG_STATUSES
from utils.models import TimeStampsModel


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
    error_message = models.TextField(null=True)
