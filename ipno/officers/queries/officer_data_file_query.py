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
        self.all_officers = officer.person.officers.all()

    def _generate_officer_sheet(self):
        officer_profile_fields = OFFICER_PROFILE_FIELDS
        officer_sheet = [{
            field: getattr(related_officer, field) for field in officer_profile_fields
        } for related_officer in self.all_officers]

        return pd.DataFrame(officer_sheet)

    def _generate_officer_incident_sheet(self):
        incidents = Event.objects.filter(officer__in=self.all_officers).annotate(
            agency=F('department__name'),
            uid=F('officer__uid'),
            uof_uid=F('use_of_force__uof_uid'),
            officer_inactive=F('event_inactive')
        ).exclude(
            kind__in=OFFICER_CAREER_KINDS
        ).values(*OFFICER_INCIDENT_FIELDS)

        return pd.DataFrame(incidents)

    def _generate_officer_complaint_sheet(self):
        complaints = Complaint.objects.filter(officers__in=self.all_officers).annotate(
            agency=F('departments__name'),
            uid=F('officers__uid'),
        ).values(*OFFICER_COMPLAINT_FIELDS)

        return pd.DataFrame(complaints)

    def _generate_officer_uof_sheet(self):
        uof = UseOfForce.objects.filter(officer__in=self.all_officers).annotate(
            agency=F('department__name'),
            uid=F('officer__uid'),
        ).values(*OFFICER_UOF_FIELDS)

        return pd.DataFrame(uof)

    def _generate_officer_career_sheet(self):
        career = Event.objects.filter(
            officer__in=self.all_officers,
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
            officers__in=self.all_officers
        ).values(*OFFICER_DOC_FIELDS)

        return pd.DataFrame(doc)

    def _write_to_sheet(self, xlsx_writer, sheet_name, dataframe):
        if not dataframe.empty:
            dataframe.dropna(how='all', axis=1, inplace=True)
            dataframe.to_excel(xlsx_writer, sheet_name, index=False)

            worksheet = xlsx_writer.sheets[sheet_name]
            worksheet.set_column('A:Z', 25)

    def generate_sheets_file(self):
        df_officer = self._generate_officer_sheet()
        df_incident = self._generate_officer_incident_sheet()
        df_complaint = self._generate_officer_complaint_sheet()
        df_uof = self._generate_officer_uof_sheet()
        df_career = self._generate_officer_career_sheet()
        df_doc = self._generate_officer_doc_sheet()

        datasheet_mapping = {
            OFFICER_PROFILE_SHEET: df_officer,
            OFFICER_INCIDENT_SHEET: df_incident,
            OFFICER_COMPLAINT_SHEET: df_complaint,
            OFFICER_UOF_SHEET: df_uof,
            OFFICER_CAREER_SHEET: df_career,
            OFFICER_DOC_SHEET: df_doc
        }

        excel_file = IO()
        xlsx_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')

        for sheet_name, dataframe in datasheet_mapping.items():
            self._write_to_sheet(xlsx_writer, sheet_name, dataframe)

        xlsx_writer.save()

        return excel_file
