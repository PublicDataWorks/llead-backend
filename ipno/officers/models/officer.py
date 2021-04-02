from django.db import models
from django.utils.functional import cached_property
from django.db.models import Prefetch

from utils.models import TimeStampsModel
from .officer_history import OfficerHistory


class OfficerManager(models.Manager):
    def prefetch_officer_histories(self):
        return self.get_queryset().prefetch_related(
            Prefetch(
                'officerhistory_set',
                queryset=OfficerHistory.objects.order_by(
                    '-start_date'
                ).prefetch_related('department')
            ),
        )


class Officer(TimeStampsModel):
    uid = models.CharField(max_length=255, unique=True, db_index=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    middle_initial = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    employee_id = models.CharField(max_length=255, null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True)
    birth_day = models.IntegerField(null=True, blank=True)
    race = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)

    departments = models.ManyToManyField('departments.Department', through='officers.OfficerHistory')

    objects = OfficerManager()

    def __str__(self):
        return f'{self.name or ""} - {self.id}'

    @property
    def name(self):
        return ' '.join([item for item in [self.first_name, self.last_name] if item])

    @property
    def badges(self):
        return [
            officer_history.badge_no for officer_history in self.officerhistory_set.all()
            if officer_history.badge_no
        ]

    @cached_property
    def document_years(self):
        return list(self.document_set.filter(
            incident_date__isnull=False,
        ).values_list('incident_date__year', flat=True))

    @cached_property
    def complaint_years(self):
        return list(self.complaint_set.filter(
            incident_date__isnull=False,
        ).values_list('incident_date__year', flat=True))
