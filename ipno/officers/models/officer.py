from django.db import models

from utils.models import TimeStampsModel


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

    departments = models.ManyToManyField('departments.Department', through='officers.OfficerHistory')

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def badges(self):
        return [
            officer_history.badge_no for officer_history in self.officerhistory_set.all()
            if officer_history.badge_no
        ]

    def __str__(self):
        return f"{self.name} - {self.id}"
