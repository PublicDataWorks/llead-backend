from django.test import TestCase

import pandas as pd

from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, EventFactory
from officers.queries import OfficerDatafileQuery
from use_of_forces.factories import UseOfForceFactory
from officers.constants import (
    COMPLAINT_RECEIVE,
    OFFICER_CAREER_SHEET,
    OFFICER_COMPLAINT_FIELDS,
    OFFICER_COMPLAINT_SHEET,
    OFFICER_DOC_FIELDS,
    OFFICER_DOC_SHEET,
    OFFICER_HIRE,
    OFFICER_INCIDENT_FIELDS,
    OFFICER_INCIDENT_SHEET,
    OFFICER_LEFT,
    OFFICER_PROFILE_FIELDS,
    OFFICER_PROFILE_SHEET,
    OFFICER_UOF_FIELDS,
    OFFICER_UOF_SHEET,
    UOF_RECEIVE,
)


class OfficerDatafileQueryTestCase(TestCase):
    def test_generate_sheets(self):
        officer = OfficerFactory()
        department = DepartmentFactory()

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_1.departments.add(department)
        complaint_2.departments.add(department)
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        document = DocumentFactory()
        document.officers.add(officer)

        uof = UseOfForceFactory(officer=officer, department=department)

        event_1 = EventFactory(
            officer=officer,
            department=department,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )
        event_2 = EventFactory(
            officer=officer,
            department=department,
            kind=OFFICER_LEFT,
            year=2020,
            month=4,
            day=8,
        )

        complaint_receive_event = EventFactory(
            officer=officer,
            department=department,
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        complaint_1.events.add(complaint_receive_event)

        uof_receive_event = EventFactory(
            officer=officer,
            department=department,
            kind=UOF_RECEIVE,
            year=2020,
            month=5,
            day=4,
            use_of_force=uof,
        )

        expected_officer_profile = [{
            key: getattr(officer, key) for key in OFFICER_PROFILE_FIELDS
        }]

        expected_document = {
            **{key: getattr(document, key) if hasattr(document, key) else {} for key in OFFICER_DOC_FIELDS},
        }

        expected_event_1 = {
            **{key: getattr(event_1, key) if hasattr(event_1, key) else {} for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
            'officer_inactive': getattr(event_1, 'event_inactive'),
        }
        expected_event_2 = {
            **{key: getattr(event_2, key) if hasattr(event_2, key) else {} for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
            'officer_inactive': getattr(event_2, 'event_inactive'),
        }
        expected_complaint_receive_event = {
            **{key: getattr(complaint_receive_event, key) if hasattr(complaint_receive_event, key) else {}
               for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
            'officer_inactive': getattr(complaint_receive_event, 'event_inactive'),
        }
        expected_uof_receive_event = {
            **{key: getattr(uof_receive_event, key) if hasattr(uof_receive_event, key) else {}
               for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': uof.uof_uid,
            'officer_inactive': getattr(uof_receive_event, 'event_inactive'),
        }

        expected_incidents = [
            expected_event_1,
            expected_event_2,
            expected_complaint_receive_event,
            expected_uof_receive_event,
        ]

        expected_career_history = [
            expected_event_1,
            expected_event_2,
        ]

        expected_complaint_1 = {
            **{key: getattr(complaint_1, key) if hasattr(complaint_1, key) else {} for key in OFFICER_COMPLAINT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
        }
        expected_complaint_2 = {
            **{key: getattr(complaint_2, key) if hasattr(complaint_2, key) else {} for key in OFFICER_COMPLAINT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
        }

        expected_complaints = [
            expected_complaint_1,
            expected_complaint_2,
        ]

        expected_uof = [{
            **{key: getattr(uof, key) if hasattr(uof, key) else {} for key in OFFICER_UOF_FIELDS},
            'report_year': str(getattr(uof, 'report_year')),
            'citizen_age': str(getattr(uof, 'citizen_age')),
            'data_production_year': str(getattr(uof, 'data_production_year')),
            'uid': officer.uid,
            'agency': department.name,
        }]

        expected_officer_sheet = pd.DataFrame(expected_officer_profile)
        expected_uof_sheet = pd.DataFrame(expected_uof)
        expected_incident_sheet = pd.DataFrame(expected_incidents)
        expected_incident_sheet_sorted = expected_incident_sheet.sort_values(by=['event_uid']).reset_index(drop=True)
        expected_career_sheet = pd.DataFrame(expected_career_history)
        expected_career_sheet_sorted = expected_career_sheet.sort_values(by=['event_uid']).reset_index(drop=True)
        expected_complaint_sheet = pd.DataFrame(expected_complaints)
        expected_complaint_sheet_sorted = expected_complaint_sheet.sort_values(by=['complaint_uid']).reset_index(drop=True)
        expected_doc_sheet = pd.DataFrame([expected_document])

        data_file = OfficerDatafileQuery(officer).generate_sheets_file()

        xlsx_officer_data = pd.read_excel(data_file, sheet_name=OFFICER_PROFILE_SHEET, dtype=str)
        xlsx_uof_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_SHEET, dtype=str)
        xlsx_incident_data = pd.read_excel(data_file, sheet_name=OFFICER_INCIDENT_SHEET)
        xlsx_incident_data_sorted = xlsx_incident_data.sort_values(by=['event_uid']).reset_index(drop=True)
        xlsx_career_data = pd.read_excel(data_file, sheet_name=OFFICER_CAREER_SHEET)
        xlsx_career_data_sorted = xlsx_career_data.sort_values(by=['event_uid']).reset_index(drop=True)
        xlsx_complaint_data = pd.read_excel(data_file, sheet_name=OFFICER_COMPLAINT_SHEET)
        xlsx_complaint_data_sorted = xlsx_complaint_data.sort_values(by=['complaint_uid']).reset_index(drop=True)
        xlsx_doc_data = pd.read_excel(data_file, sheet_name=OFFICER_DOC_SHEET, dtype=str)

        pd.testing.assert_frame_equal(xlsx_officer_data, expected_officer_sheet)
        pd.testing.assert_frame_equal(xlsx_uof_data, expected_uof_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_doc_data, expected_doc_sheet, check_like=True)

        pd.testing.assert_frame_equal(xlsx_incident_data_sorted, expected_incident_sheet_sorted, check_like=True,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(xlsx_career_data_sorted, expected_career_sheet_sorted, check_like=True,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(xlsx_complaint_data_sorted, expected_complaint_sheet_sorted, check_like=True,
                                      check_dtype=False)