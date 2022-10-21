from django.db import models

from utils.models import TimeStampsModel


class Complaint(TimeStampsModel):
    allegation_uid = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    uid = models.CharField(max_length=255, null=True, blank=True)
    case_number = models.CharField(max_length=255, null=True, blank=True)
    allegation = models.TextField(null=True, blank=True)
    investigation_status = models.CharField(max_length=255, null=True, blank=True)
    assigned_department = models.CharField(max_length=255, null=True, blank=True)
    assigned_division = models.CharField(max_length=255, null=True, blank=True)
    traffic_stop = models.CharField(max_length=255, null=True, blank=True)
    body_worn_camera_available = models.CharField(max_length=255, null=True, blank=True)
    app_used = models.CharField(max_length=255, null=True, blank=True)
    citizen_arrested = models.CharField(max_length=255, null=True, blank=True)
    citizen = models.CharField(max_length=255, null=True, blank=True)
    disposition = models.CharField(max_length=255, null=True, blank=True)
    complainant_name = models.CharField(max_length=255, null=True, blank=True)
    complainant_type = models.CharField(max_length=255, null=True, blank=True)
    complainant_sex = models.CharField(max_length=255, null=True, blank=True)
    complainant_race = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    initial_action = models.CharField(max_length=255, null=True, blank=True)
    incident_type = models.CharField(max_length=255, null=True, blank=True)
    supervisor_uid = models.CharField(max_length=255, null=True, blank=True)
    supervisor_rank = models.CharField(max_length=255, null=True, blank=True)
    badge_no = models.CharField(max_length=255, null=True, blank=True)
    department_code = models.CharField(max_length=255, null=True, blank=True)
    department_desc = models.CharField(max_length=255, null=True, blank=True)
    employment_status = models.CharField(max_length=255, null=True, blank=True)
    investigator = models.CharField(max_length=255, null=True, blank=True)
    investigator_uid = models.CharField(max_length=255, null=True, blank=True)
    investigator_rank = models.CharField(max_length=255, null=True, blank=True)
    shift_supervisor = models.CharField(max_length=255, null=True, blank=True)
    allegation_desc = models.TextField(null=True, blank=True)
    investigating_department = models.CharField(max_length=255, null=True, blank=True)
    referred_by = models.CharField(max_length=255, null=True, blank=True)
    incident_location = models.CharField(max_length=255, null=True, blank=True)
    disposition_desc = models.CharField(max_length=255, null=True, blank=True)

    officers = models.ManyToManyField('officers.Officer', blank=True, related_name='complaints')
    departments = models.ManyToManyField('departments.Department', blank=True, related_name='complaints')
    events = models.ManyToManyField('officers.Event', blank=True, related_name='complaints')

    class Meta:
        unique_together = ('allegation_uid',)

    def __str__(self):
        return f'{self.id} - {self.allegation_uid[:5]}'
