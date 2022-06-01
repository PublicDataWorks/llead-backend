from django.db import models

from utils.models import TimeStampsModel


class UseOfForceOfficer(TimeStampsModel):
    uof_uid = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    use_of_force_description = models.CharField(max_length=255, null=True, blank=True)
    use_of_force_level = models.CharField(max_length=255, null=True, blank=True)
    use_of_force_effective = models.CharField(max_length=255, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    years_of_service = models.IntegerField(null=True, blank=True)
    officer_injured = models.CharField(max_length=255, null=True, blank=True)

    officer = models.ForeignKey('officers.Officer', on_delete=models.CASCADE, null=True, related_name='uof_officers')
    use_of_force = models.ForeignKey(
        'use_of_forces.UseOfForce', on_delete=models.CASCADE, null=True, related_name='uof_officers'
    )

    class Meta:
        unique_together = ('uof_uid', 'uid',)
