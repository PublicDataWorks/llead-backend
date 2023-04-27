from django.core.exceptions import ValidationError
from django.db import models

from utils.models import TimeStampsModel


class Finding(TimeStampsModel):
    background_image = models.ImageField(upload_to="background/", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    card_image = models.ImageField(upload_to="card/", null=True, blank=True)
    card_title = models.CharField(max_length=255, null=True, blank=True)
    card_author = models.CharField(max_length=255, null=True, blank=True)
    card_department = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):  # pragma: no cover
        if not self.pk and Finding.objects.exists():
            raise ValidationError("There is only one Finding instance")

        return super(Finding, self).save(*args, **kwargs)
