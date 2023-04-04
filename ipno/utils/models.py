from django.db import models


class TimeStampsModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class APITemplateModel(models.Model):
    BASE_FIELDS = {"id", "created_at", "updated_at"}

    class Meta:
        abstract = True
