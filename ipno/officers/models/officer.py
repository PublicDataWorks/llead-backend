from django.db import models
from django.utils.functional import cached_property
from django.db.models import Prefetch, F

from utils.models import TimeStampsModel
from officers.models.event import Event


class OfficerManager(models.Manager):
    def prefetch_events(self, other_prefetches=()):
        return self.get_queryset().prefetch_related(
            Prefetch(
                'person__officers__events',
                queryset=Event.objects.order_by(
                    F('year').desc(nulls_last=True),
                    F('month').desc(nulls_last=True),
                    F('day').desc(nulls_last=True),
                ).prefetch_related('department')
            ),
            *other_prefetches
        )


class Officer(TimeStampsModel):
    uid = models.CharField(max_length=255, unique=True, db_index=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    birth_month = models.IntegerField(null=True, blank=True)
    birth_day = models.IntegerField(null=True, blank=True)
    race = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(max_length=255, null=True, blank=True)

    is_name_changed = models.BooleanField(default=False)

    departments = models.ManyToManyField('departments.Department', through='officers.Event')
    person = models.ForeignKey(
        'people.Person',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='officers'
    )
    objects = OfficerManager()

    def __str__(self):
        return f'{self.name or ""} - {self.id}'

    @property
    def name(self):
        return ' '.join([item for item in [self.first_name, self.last_name] if item])

    @property
    def badges(self):
        return list(dict.fromkeys([
            event.badge_no for event in self.events.all()
            if event.badge_no
        ]))

    @cached_property
    def document_years(self):
        return list(self.documents.filter(
            incident_date__isnull=False,
        ).values_list('incident_date__year', flat=True))
