from io import BytesIO as IO

from django.db.models import F

import pandas as pd

from complaints.models import Complaint
from documents.models import Document
from officers.models import Event
from use_of_forces.models import UseOfForce
from officers.constants import (
    OFFICER_CAREER_KINDS,
    OFFICER_CAREER_SHEET,
    OFFICER_COMPLAINT_FIELDS,
    OFFICER_COMPLAINT_SHEET,
    OFFICER_DOC_FIELDS,
    OFFICER_DOC_SHEET,
    OFFICER_INCIDENT_FIELDS,
    OFFICER_INCIDENT_SHEET,
    OFFICER_PROFILE_FIELDS,
    OFFICER_PROFILE_SHEET,
    OFFICER_UOF_FIELDS,
    OFFICER_UOF_SHEET,
)


class OfficerDatafileQuery(object):
    def __init__(self, officer):
        self.officer = officer

    def _generate_officer_sheet(self):
        officer_profile_fields = OFFICER_PROFILE_FIELDS
        officer_sheet = {
            field: getattr(self.officer, field) for field in officer_profile_fields
        }

        return pd.DataFrame([officer_sheet])

    def _generate_officer_incident_sheet(self):
        incidents = Event.objects.filter(officer=self.officer).annotate(
            agency=F('department__name'),
            uid=F('officer__uid'),
            uof_uid=F('use_of_force__uof_uid'),
            officer_inactive=F('event_inactive')
        ).exclude(
            kind__in=OFFICER_CAREER_KINDS
        ).values(*OFFICER_INCIDENT_FIELDS)

        return pd.DataFrame(incidents)

    def _generate_officer_complaint_sheet(self):
        complaints = Complaint.objects.filter(officers__in=[self.officer]).annotate(
            agency=F('departments__name'),
            uid=F('officers__uid'),
        ).values(*OFFICER_COMPLAINT_FIELDS)

        return pd.DataFrame(complaints)

    def _generate_officer_uof_sheet(self):
        uof = UseOfForce.objects.filter(officer=self.officer).annotate(
            agency=F('department__name'),
            uid=F('officer__uid'),
        ).values(*OFFICER_UOF_FIELDS)

        return pd.DataFrame(uof)

    def _generate_officer_career_sheet(self):
        career = Event.objects.filter(
            officer=self.officer,
            kind__in=OFFICER_CAREER_KINDS
        ).annotate(
            agency=F('department__name'),
            uid=F('officer__uid'),
            uof_uid=F('use_of_force__uof_uid'),
            officer_inactive=F('event_inactive')
        ).values(*OFFICER_INCIDENT_FIELDS)

        return pd.DataFrame(career)

    def _generate_officer_doc_sheet(self):
        doc = Document.objects.filter(
            officers__in=[self.officer]
        ).values(*OFFICER_DOC_FIELDS)

        return pd.DataFrame(doc)

    def generate_sheets_file(self):
        df_officer = self._generate_officer_sheet()
        df_incident = self._generate_officer_incident_sheet()
        df_complaint = self._generate_officer_complaint_sheet()
        df_uof = self._generate_officer_uof_sheet()
        df_career = self._generate_officer_career_sheet()
        df_doc = self._generate_officer_doc_sheet()

        excel_file = IO()
        xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')

        df_officer.to_excel(xlwriter, OFFICER_PROFILE_SHEET, index=False)
        df_incident.to_excel(xlwriter, OFFICER_INCIDENT_SHEET, index=False)
        df_complaint.to_excel(xlwriter, OFFICER_COMPLAINT_SHEET, index=False)
        df_uof.to_excel(xlwriter, OFFICER_UOF_SHEET, index=False)
        df_career.to_excel(xlwriter, OFFICER_CAREER_SHEET, index=False)
        df_doc.to_excel(xlwriter, OFFICER_DOC_SHEET, index=False)

        xlwriter.save()

        return excel_file
