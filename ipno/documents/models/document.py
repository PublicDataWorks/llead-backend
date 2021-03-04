from django.db import models
from django.db.models import Prefetch, F

from utils.models import TimeStampsModel
from officers.models import OfficerHistory


class DocumentManager(models.Manager):
    def prefetch_departments(self):
        officer_histories = OfficerHistory.objects.filter(
            start_date__isnull=False,
            end_date__isnull=False,
            officer__document__incident_date__isnull=False,
            start_date__lte=F('officer__document__incident_date'),
            end_date__gte=F('officer__document__incident_date'),
        ).prefetch_related('department')

        return self.get_queryset().prefetch_related(
            'departments',
            Prefetch(
                'officers__officerhistory_set',
                queryset=officer_histories,
                to_attr='prefetched_officer_histories'
            )
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
