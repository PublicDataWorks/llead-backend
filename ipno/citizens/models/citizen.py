from django.db import models

from utils.models import APITemplateModel, TimeStampsModel


class Citizen(TimeStampsModel, APITemplateModel):
    CUSTOM_FIELDS = {"use_of_force", "complaint", "department"}

    citizen_uid = models.CharField(max_length=255)
    allegation_uid = models.CharField(max_length=255, null=True, blank=True)
    uof_uid = models.CharField(max_length=255, null=True, blank=True)
    citizen_influencing_factors = models.CharField(
        max_length=255, null=True, blank=True
    )
    citizen_arrested = models.CharField(max_length=255, null=True, blank=True)
    citizen_hospitalized = models.CharField(max_length=255, null=True, blank=True)
    citizen_injured = models.CharField(max_length=255, null=True, blank=True)
    citizen_age = models.IntegerField(null=True, blank=True)
    citizen_race = models.CharField(max_length=255, null=True, blank=True)
    citizen_sex = models.CharField(max_length=255, null=True, blank=True)
    agency = models.CharField(max_length=255, null=True, blank=True)

    use_of_force = models.ForeignKey(
        "use_of_forces.UseOfForce",
        on_delete=models.CASCADE,
        null=True,
        related_name="citizens",
    )
    complaint = models.ForeignKey(
        "complaints.Complaint",
        on_delete=models.CASCADE,
        null=True,
        related_name="citizens",
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.CASCADE,
        null=True,
        related_name="citizens",
    )
