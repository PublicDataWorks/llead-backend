from django.db import models

from utils.models import TimeStampsModel


class UseOfForceCitizen(TimeStampsModel):
    uof_citizen_uid = models.CharField(max_length=255)
    uof_uid = models.CharField(max_length=255)
    citizen_influencing_factors = models.CharField(max_length=255, null=True, blank=True)
    citizen_distance_from_officer = models.CharField(max_length=255, null=True, blank=True)
    citizen_arrested = models.CharField(max_length=255, null=True, blank=True)
    citizen_arrest_charges = models.CharField(max_length=255, null=True, blank=True)
    citizen_hospitalized = models.CharField(max_length=255, null=True, blank=True)
    citizen_injured = models.CharField(max_length=255, null=True, blank=True)
    citizen_age = models.CharField(max_length=255, null=True, blank=True)
    citizen_race = models.CharField(max_length=255, null=True, blank=True)
    citizen_sex = models.CharField(max_length=255, null=True, blank=True)

    use_of_force = models.ForeignKey(
        'use_of_forces.UseOfForce', on_delete=models.CASCADE, null=True, related_name='uof_citizens'
    )
