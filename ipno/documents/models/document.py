from django.db import models

from utils.models import TimeStampsModel


class DocumentManager(models.Manager):
    def prefetch_departments(self):
        return self.get_queryset().prefetch_related(
            'departments',
        )


class Document(TimeStampsModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    document_type = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    preview_image_url = models.CharField(max_length=255, null=True, blank=True)
    incident_date = models.DateField(null=True, blank=True)
    pages_count = models.IntegerField(null=True, blank=True)
    text_content = models.TextField(blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True)
    departments = models.ManyToManyField('departments.Department', blank=True)

    objects = DocumentManager()
