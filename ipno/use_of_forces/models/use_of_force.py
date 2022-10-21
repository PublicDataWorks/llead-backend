from django.db import models

from utils.models import TimeStampsModel


class UseOfForce(TimeStampsModel):
    uof_uid = models.CharField(max_length=255, unique=True, db_index=True)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    investigation_status = models.CharField(max_length=255, null=True, blank=True)
    service_type = models.CharField(max_length=255, null=True, blank=True)
    light_condition = models.CharField(max_length=255, null=True, blank=True)
    weather_condition = models.CharField(max_length=255, null=True, blank=True)
    shift_time = models.CharField(max_length=255, null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    division = models.CharField(max_length=255, null=True, blank=True)
    division_level = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=255, null=True, blank=True)
    originating_bureau = models.CharField(max_length=255, null=True, blank=True)
    agency = models.CharField(max_length=255, null=True, blank=True)
    use_of_force_reason = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField(
        'officers.Officer',
        through='use_of_forces.UseOfForceOfficer',
        related_name='use_of_forces'
    )
    department = models.ForeignKey(
        'departments.Department', on_delete=models.CASCADE, null=True, related_name='use_of_forces'
    )

    def __str__(self):
        return f'{self.id} - {self.uof_uid[:5]}'
