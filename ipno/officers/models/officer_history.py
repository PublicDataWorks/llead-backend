from django.db import models

from utils.models import TimeStampsModel


class OfficerHistory(TimeStampsModel):
    officer = models.ForeignKey('officers.Officer', on_delete=models.CASCADE, null=True)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    badge_no = models.CharField(max_length=255, null=True, blank=True)
    department_code = models.CharField(max_length=255, null=True, blank=True)
    department_desc = models.CharField(max_length=255, null=True, blank=True)
    data_production_year = models.IntegerField(null=True, blank=True)
    rank_code = models.CharField(max_length=255, null=True, blank=True)
    rank_desc = models.CharField(max_length=255, null=True, blank=True)
    rank_year = models.IntegerField(null=True, blank=True)
    rank_month = models.IntegerField(null=True, blank=True)
    rank_day = models.IntegerField(null=True, blank=True)
    hire_year = models.IntegerField(null=True, blank=True)
    hire_month = models.IntegerField(null=True, blank=True)
    hire_day = models.IntegerField(null=True, blank=True)
    term_year = models.IntegerField(null=True, blank=True)
    term_month = models.IntegerField(null=True, blank=True)
    term_day = models.IntegerField(null=True, blank=True)
    pay_effective_year = models.IntegerField(null=True, blank=True)
    pay_effective_month = models.IntegerField(null=True, blank=True)
    pay_effective_day = models.IntegerField(null=True, blank=True)
    annual_salary = models.CharField(max_length=255, null=True, blank=True)
    hourly_salary = models.CharField(max_length=255, null=True, blank=True)
