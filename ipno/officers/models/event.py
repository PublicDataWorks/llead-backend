from django.db import models

from utils.models import TimeStampsModel
from officers.constants import EVENT_KINDS


class Event(TimeStampsModel):
    event_uid = models.CharField(max_length=255, db_index=True)
    kind = models.CharField(max_length=255, choices=EVENT_KINDS, db_index=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    month = models.IntegerField(null=True, blank=True, db_index=True)
    day = models.IntegerField(null=True, blank=True, db_index=True)
    time = models.CharField(max_length=255, null=True, blank=True)
    raw_date = models.CharField(max_length=255, null=True, blank=True)
    complaint_uid = models.CharField(max_length=255, null=True, blank=True)
    allegation_uid = models.CharField(max_length=255, null=True, blank=True)
    appeal_uid = models.CharField(max_length=255, null=True, blank=True)
    use_of_force_uid = models.CharField(max_length=255, null=True, blank=True)
    badge_no = models.CharField(max_length=255, null=True, blank=True)
    employee_id = models.CharField(max_length=255, null=True, blank=True)
    department_code = models.CharField(max_length=255, null=True, blank=True)
    department_desc = models.CharField(max_length=255, null=True, blank=True)
    division_desc = models.CharField(max_length=255, null=True, blank=True)
    sub_division_a_desc = models.CharField(max_length=255, null=True, blank=True)
    sub_division_b_desc = models.CharField(max_length=255, null=True, blank=True)
    current_supervisor = models.CharField(max_length=255, null=True, blank=True)
    rank_code = models.CharField(max_length=255, null=True, blank=True)
    rank_desc = models.CharField(max_length=255, null=True, blank=True)
    employment_status = models.CharField(max_length=255, null=True, blank=True)
    officer_inactive = models.CharField(max_length=255, null=True, blank=True)
    employee_type = models.CharField(max_length=255, null=True, blank=True)
    years_employed = models.IntegerField(null=True, blank=True)
    annual_salary = models.CharField(max_length=255, null=True, blank=True)
    hourly_salary = models.CharField(max_length=255, null=True, blank=True)

    officer = models.ForeignKey('officers.Officer', on_delete=models.CASCADE, null=True)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, null=True)
