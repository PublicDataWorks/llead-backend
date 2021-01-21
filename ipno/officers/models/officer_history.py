from django.db import models

from utils.models import TimeStampsModel


class OfficerHistory(TimeStampsModel):
    officer = models.ForeignKey('officers.Officer', on_delete=models.CASCADE, null=True)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, null=True)

    badge_no = models.CharField(max_length=255, null=True, blank=True)
    rank_code = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
