from django.db import models

from utils.models import TimeStampsModel


class CrawledPost(TimeStampsModel):
    source_name = models.CharField(max_length=255)
    post_guid = models.CharField(max_length=255)
