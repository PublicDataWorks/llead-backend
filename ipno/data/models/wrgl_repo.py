from django.db import models

from utils.models import TimeStampsModel


class WrglRepo(TimeStampsModel):
    data_model = models.CharField(max_length=255, unique=True)
    repo_name = models.CharField(max_length=255)
    commit_hash = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.repo_name}-{self.data_model}'
