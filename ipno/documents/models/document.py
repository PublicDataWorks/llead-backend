from django.db import models

from utils.models import TimeStampsModel


class DocumentManager(models.Manager):
    def prefetch_departments(self):
        return self.get_queryset().prefetch_related(
            'departments',
        )


class Document(TimeStampsModel):
    docid = models.CharField(max_length=255, null=True, blank=True)
    hrg_no = models.CharField(max_length=255, null=True, blank=True)
    matched_uid = models.CharField(max_length=255, null=True, blank=True)
    fileid = models.CharField(max_length=255, null=True, blank=True)
    file_db_path = models.CharField(max_length=255, null=True, blank=True)
    file_db_content_hash = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    document_type = models.CharField(max_length=255, null=True, blank=True)
    url = models.CharField(max_length=255, null=True, blank=True)
    preview_image_url = models.CharField(max_length=255, null=True, blank=True)
    incident_date = models.DateField(null=True, blank=True)
    pages_count = models.IntegerField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    accused = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True, related_name='documents')
    departments = models.ManyToManyField('departments.Department', blank=True, related_name='documents')

    objects = DocumentManager()

    class Meta:
        unique_together = ('docid', 'hrg_no', 'matched_uid')
