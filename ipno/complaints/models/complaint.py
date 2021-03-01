from django.db import models

from utils.models import TimeStampsModel


class Complaint(TimeStampsModel):
    incident_date = models.DateField(null=True)
    tracking_number = models.CharField(max_length=255, null=True, blank=True)
    occur_year = models.IntegerField(null=True, blank=True)
    occur_month = models.IntegerField(null=True, blank=True)
    occur_day = models.IntegerField(null=True, blank=True)
    occur_time = models.CharField(max_length=255, null=True, blank=True)
    receive_year = models.IntegerField(null=True, blank=True)
    receive_month = models.IntegerField(null=True, blank=True)
    receive_day = models.IntegerField(null=True, blank=True)
    suspension_start_year = models.IntegerField(null=True, blank=True)
    suspension_start_month = models.IntegerField(null=True, blank=True)
    suspension_start_day = models.IntegerField(null=True, blank=True)
    suspension_end_year = models.IntegerField(null=True, blank=True)
    suspension_end_month = models.IntegerField(null=True, blank=True)
    suspension_end_day = models.IntegerField(null=True, blank=True)
    investigation_status = models.CharField(max_length=255, null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    rule_code = models.CharField(max_length=255, null=True, blank=True)
    rule_violation = models.CharField(max_length=255, null=True, blank=True)
    paragraph_code = models.CharField(max_length=255, null=True, blank=True)
    paragraph_violation = models.CharField(max_length=255, null=True, blank=True)
    complainant_name = models.CharField(max_length=255, null=True, blank=True)
    complainant_sex = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    complainant_type = models.CharField(max_length=255, null=True, blank=True)
    data_production_year = models.CharField(max_length=255, null=True, blank=True)
    supervisor_uid = models.CharField(max_length=255, null=True, blank=True)
    supervisor_rank = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True)
    departments = models.ManyToManyField('departments.Department', blank=True)
