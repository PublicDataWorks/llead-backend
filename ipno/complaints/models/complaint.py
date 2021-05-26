from django.db import models

from utils.models import TimeStampsModel


class Complaint(TimeStampsModel):
    complaint_uid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    allegation_uid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    charge_uid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    tracking_number = models.CharField(max_length=255, null=True, blank=True)
    investigation_type = models.CharField(max_length=255, null=True, blank=True)
    investigation_status = models.CharField(max_length=255, null=True, blank=True)
    assigned_unit = models.CharField(max_length=255, null=True, blank=True)
    assigned_department = models.CharField(max_length=255, null=True, blank=True)
    assigned_division = models.CharField(max_length=255, null=True, blank=True)
    assigned_sub_division_a = models.CharField(max_length=255, null=True, blank=True)
    body_worn_camera_available = models.CharField(max_length=255, null=True, blank=True)
    app_used = models.CharField(max_length=255, null=True, blank=True)
    citizen_arrested = models.CharField(max_length=255, null=True, blank=True)
    allegation_finding = models.CharField(max_length=255, null=True, blank=True)
    allegation = models.CharField(max_length=255, null=True, blank=True)
    allegation_class = models.CharField(max_length=255, null=True, blank=True)
    citizen = models.CharField(max_length=255, null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    rule_code = models.CharField(max_length=255, null=True, blank=True)
    rule_violation = models.CharField(max_length=255, null=True, blank=True)
    paragraph_code = models.CharField(max_length=255, null=True, blank=True)
    paragraph_violation = models.CharField(max_length=255, null=True, blank=True)
    charges = models.TextField(null=True, blank=True)
    complainant_type = models.CharField(max_length=255, null=True, blank=True)
    complainant_sex = models.CharField(max_length=255, null=True, blank=True)
    complainant_race = models.CharField(max_length=255, null=True, blank=True)
    recommended_action = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    data_production_year = models.IntegerField(null=True, blank=True)
    incident_type = models.CharField(max_length=255, null=True, blank=True)
    supervisor_uid = models.CharField(max_length=255, null=True, blank=True)
    supervisor_rank = models.CharField(max_length=255, null=True, blank=True)
    badge_no = models.CharField(max_length=255, null=True, blank=True)
    department_code = models.CharField(max_length=255, null=True, blank=True)
    department_desc = models.CharField(max_length=255, null=True, blank=True)
    rank_desc = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True, related_name='complaints')
    departments = models.ManyToManyField('departments.Department', blank=True, related_name='complaints')
    events = models.ManyToManyField('officers.Event', blank=True, related_name='complaints')

    class Meta:
        unique_together = ('complaint_uid', 'allegation_uid', 'charge_uid')
