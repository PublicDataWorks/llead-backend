from django.db import models

from utils.models import TimeStampsModel


class Person(TimeStampsModel):
    person_id = models.CharField(max_length=255, null=True, blank=True)

    canonical_officer = models.ForeignKey(
        'officers.Officer',
        on_delete=models.CASCADE,
        related_name='canonical_person',
    )
