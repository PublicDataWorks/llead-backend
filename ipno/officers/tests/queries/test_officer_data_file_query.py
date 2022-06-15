from django.test import TestCase

import pandas as pd

from complaints.factories import ComplaintFactory
from departments.factories import DepartmentFactory
from documents.factories import DocumentFactory
from officers.factories import OfficerFactory, EventFactory
from officers.queries import OfficerDatafileQuery
from people.factories import PersonFactory
from use_of_forces.factories import UseOfForceFactory, UseOfForceOfficerFactory, UseOfForceCitizenFactory
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
    OFFICER_UOF_OFFICER_FIELDS,
    OFFICER_UOF_CITIZEN_FIELDS,
    OFFICER_UOF_OFFICER_SHEET,
    OFFICER_UOF_CITIZEN_SHEET,
)


class OfficerDatafileQueryTestCase(TestCase):
    def test_generate_sheets(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        department = DepartmentFactory()

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_1.departments.add(department)
        complaint_2.departments.add(department)
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        document = DocumentFactory()
        document.officers.add(officer)

        uof = UseOfForceFactory(department=department)
        uof_officer = UseOfForceOfficerFactory(officer=officer, use_of_force=uof)
        uof_citizen = UseOfForceCitizenFactory(use_of_force=uof)

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
        }
        expected_event_2 = {
            **{key: getattr(event_2, key) if hasattr(event_2, key) else {} for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
        }
        expected_complaint_receive_event = {
            **{key: getattr(complaint_receive_event, key) if hasattr(complaint_receive_event, key) else {}
               for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
        }
        expected_uof_receive_event = {
            **{key: getattr(uof_receive_event, key) if hasattr(uof_receive_event, key) else {}
               for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': uof.uof_uid,
        }

        expected_incidents = [
            expected_complaint_receive_event,
            expected_uof_receive_event,
        ]

        expected_career_history = [
            expected_event_1,
            expected_event_2,
        ]

        expected_complaint_1 = {
            **{key: getattr(complaint_1, key) if hasattr(complaint_1, key) else {} for key in OFFICER_COMPLAINT_FIELDS},
            'agency': department.name,
        }
        expected_complaint_2 = {
            **{key: getattr(complaint_2, key) if hasattr(complaint_2, key) else {} for key in OFFICER_COMPLAINT_FIELDS},
            'agency': department.name,
        }

        expected_complaints = [
            expected_complaint_1,
            expected_complaint_2,
        ]

        expected_uof = [{
            **{key: getattr(uof, key) if hasattr(uof, key) else {} for key in OFFICER_UOF_FIELDS},
        }]

        expected_uof_officer = [{
            **{key: getattr(uof_officer, key) if hasattr(uof_officer, key) else {}
               for key in OFFICER_UOF_OFFICER_FIELDS},
        }]

        expected_uof_citizen = [{
            **{key: getattr(uof_citizen, key) if hasattr(uof_citizen, key) else {}
               for key in OFFICER_UOF_CITIZEN_FIELDS},
        }]

        expected_officer_sheet = pd.DataFrame(expected_officer_profile)
        expected_officer_sheet.dropna(how='all', axis=1, inplace=True)
        expected_uof_sheet = pd.DataFrame(expected_uof)
        expected_uof_sheet.dropna(how='all', axis=1, inplace=True)
        expected_uof_officer_sheet = pd.DataFrame(expected_uof_officer)
        expected_uof_officer_sheet.dropna(how='all', axis=1, inplace=True)
        expected_uof_citizen_sheet = pd.DataFrame(expected_uof_citizen)
        expected_uof_citizen_sheet.dropna(how='all', axis=1, inplace=True)
        expected_incident_sheet = pd.DataFrame(expected_incidents)
        expected_incident_sheet_sorted = expected_incident_sheet.sort_values(by=['event_uid']).reset_index(drop=True)
        expected_incident_sheet_sorted.dropna(how='all', axis=1, inplace=True)
        expected_career_sheet = pd.DataFrame(expected_career_history)
        expected_career_sheet_sorted = expected_career_sheet.sort_values(by=['event_uid']).reset_index(drop=True)
        expected_career_sheet_sorted.dropna(how='all', axis=1, inplace=True)
        expected_complaint_sheet = pd.DataFrame(expected_complaints)
        expected_complaint_sheet_sorted = expected_complaint_sheet.sort_values(by=['allegation_uid']).reset_index(drop=True)
        expected_complaint_sheet_sorted.dropna(how='all', axis=1, inplace=True)
        expected_doc_sheet = pd.DataFrame([expected_document])
        expected_doc_sheet.dropna(how='all', axis=1, inplace=True)

        data_file = OfficerDatafileQuery(officer).generate_sheets_file()

        xlsx_officer_data = pd.read_excel(data_file, sheet_name=OFFICER_PROFILE_SHEET, dtype=str)
        xlsx_uof_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_SHEET, dtype=str)
        xlsx_uof_officer_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_OFFICER_SHEET)
        xlsx_uof_citizen_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_CITIZEN_SHEET)
        xlsx_incident_data = pd.read_excel(data_file, sheet_name=OFFICER_INCIDENT_SHEET)
        xlsx_incident_data_sorted = xlsx_incident_data.sort_values(by=['event_uid']).reset_index(drop=True)
        xlsx_career_data = pd.read_excel(data_file, sheet_name=OFFICER_CAREER_SHEET)
        xlsx_career_data_sorted = xlsx_career_data.sort_values(by=['event_uid']).reset_index(drop=True)
        xlsx_complaint_data = pd.read_excel(data_file, sheet_name=OFFICER_COMPLAINT_SHEET)
        xlsx_complaint_data_sorted = xlsx_complaint_data.sort_values(by=['allegation_uid']).reset_index(drop=True)
        xlsx_doc_data = pd.read_excel(data_file, sheet_name=OFFICER_DOC_SHEET, dtype=str)

        def lstrip0(row):
            row.birth_month = row.birth_month.lstrip('0')
            row.birth_day = row.birth_day.lstrip('0')
            return row

        expected_officer_sheet_strip = expected_officer_sheet.apply(lstrip0, axis='columns')

        pd.testing.assert_frame_equal(xlsx_officer_data, expected_officer_sheet_strip)
        pd.testing.assert_frame_equal(xlsx_uof_data, expected_uof_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_uof_officer_data, expected_uof_officer_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_uof_citizen_data, expected_uof_citizen_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_doc_data, expected_doc_sheet, check_like=True)

        pd.testing.assert_frame_equal(xlsx_incident_data_sorted, expected_incident_sheet_sorted, check_like=True,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(xlsx_career_data_sorted, expected_career_sheet_sorted, check_like=True,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(xlsx_complaint_data_sorted, expected_complaint_sheet_sorted, check_like=True,
                                      check_dtype=False)

    def test_do_not_generate_sheets_with_empty_dataframe(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        expected_officer_profile = [{
            key: getattr(officer, key) for key in OFFICER_PROFILE_FIELDS
        }]

        expected_officer_sheet = pd.DataFrame(expected_officer_profile)
        expected_officer_sheet.dropna(how='all', axis=1, inplace=True)

        data_file = OfficerDatafileQuery(officer).generate_sheets_file()

        xlsx_officer_data = pd.read_excel(data_file, sheet_name=OFFICER_PROFILE_SHEET, dtype=str)

        no_of_sheets = len(pd.read_excel(data_file))

        def lstrip0(row):
            row.birth_month = row.birth_month.lstrip('0')
            row.birth_day = row.birth_day.lstrip('0')
            return row

        expected_officer_sheet_strip = expected_officer_sheet.apply(lstrip0, axis='columns')

        pd.testing.assert_frame_equal(xlsx_officer_data, expected_officer_sheet_strip)
        assert no_of_sheets == 1

    def test_generate_sheets_with_related_officer(self):
        person = PersonFactory()
        officer = OfficerFactory(person=person)
        related_officer = OfficerFactory(person=person)
        person.canonical_officer = officer
        person.save()

        department = DepartmentFactory()

        complaint_1 = ComplaintFactory()
        complaint_2 = ComplaintFactory()
        complaint_1.departments.add(department)
        complaint_2.departments.add(department)
        complaint_1.officers.add(officer)
        complaint_2.officers.add(related_officer)

        document = DocumentFactory()
        document.officers.add(officer)

        uof = UseOfForceFactory(department=department)
        uof_officer = UseOfForceOfficerFactory(officer=related_officer, use_of_force=uof)
        uof_citizen = UseOfForceCitizenFactory(use_of_force=uof)

        event_1 = EventFactory(
            officer=officer,
            department=department,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )
        event_2 = EventFactory(
            officer=related_officer,
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
            officer=related_officer,
            department=department,
            kind=UOF_RECEIVE,
            year=2020,
            month=5,
            day=4,
            use_of_force=uof,
        )

        expected_officer_profile = [
            {
                key: getattr(officer, key) for key in OFFICER_PROFILE_FIELDS
            },
            {
                key: getattr(related_officer, key) for key in OFFICER_PROFILE_FIELDS
            }
        ]

        expected_document = {
            **{key: getattr(document, key) if hasattr(document, key) else {} for key in OFFICER_DOC_FIELDS},
        }

        expected_event_1 = {
            **{key: getattr(event_1, key) if hasattr(event_1, key) else {} for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
        }
        expected_event_2 = {
            **{key: getattr(event_2, key) if hasattr(event_2, key) else {} for key in OFFICER_INCIDENT_FIELDS},
            'uid': related_officer.uid,
            'agency': department.name,
            'uof_uid': None,
        }
        expected_complaint_receive_event = {
            **{key: getattr(complaint_receive_event, key) if hasattr(complaint_receive_event, key) else {}
               for key in OFFICER_INCIDENT_FIELDS},
            'uid': officer.uid,
            'agency': department.name,
            'uof_uid': None,
        }
        expected_uof_receive_event = {
            **{key: getattr(uof_receive_event, key) if hasattr(uof_receive_event, key) else {}
               for key in OFFICER_INCIDENT_FIELDS},
            'uid': related_officer.uid,
            'agency': department.name,
            'uof_uid': uof.uof_uid,
        }

        expected_incidents = [
            expected_complaint_receive_event,
            expected_uof_receive_event,
        ]

        expected_career_history = [
            expected_event_1,
            expected_event_2,
        ]

        expected_complaint_1 = {
            **{key: getattr(complaint_1, key) if hasattr(complaint_1, key) else {} for key in OFFICER_COMPLAINT_FIELDS},
            'agency': department.name,
        }
        expected_complaint_2 = {
            **{key: getattr(complaint_2, key) if hasattr(complaint_2, key) else {} for key in OFFICER_COMPLAINT_FIELDS},
            'agency': department.name,
        }

        expected_complaints = [
            expected_complaint_1,
            expected_complaint_2,
        ]

        expected_uof = [{
            **{key: getattr(uof, key) if hasattr(uof, key) else {} for key in OFFICER_UOF_FIELDS},
        }]

        expected_uof_officer = [{
            **{key: getattr(uof_officer, key) if hasattr(uof_officer, key) else {}
                for key in OFFICER_UOF_OFFICER_FIELDS},
        }]

        expected_uof_citizen = [{
            **{key: getattr(uof_citizen, key) if hasattr(uof_citizen, key) else {}
                for key in OFFICER_UOF_CITIZEN_FIELDS},
        }]

        expected_officer_sheet = pd.DataFrame(expected_officer_profile)
        expected_officer_sheet.dropna(how='all', axis=1, inplace=True)
        expected_uof_sheet = pd.DataFrame(expected_uof)
        expected_uof_sheet.dropna(how='all', axis=1, inplace=True)
        expected_uof_officer_sheet = pd.DataFrame(expected_uof_officer)
        expected_uof_officer_sheet.dropna(how='all', axis=1, inplace=True)
        expected_uof_citizen_sheet = pd.DataFrame(expected_uof_citizen)
        expected_uof_citizen_sheet.dropna(how='all', axis=1, inplace=True)
        expected_incident_sheet = pd.DataFrame(expected_incidents)
        expected_incident_sheet_sorted = expected_incident_sheet.sort_values(by=['event_uid']).reset_index(drop=True)
        expected_incident_sheet_sorted.dropna(how='all', axis=1, inplace=True)
        expected_career_sheet = pd.DataFrame(expected_career_history)
        expected_career_sheet_sorted = expected_career_sheet.sort_values(by=['event_uid']).reset_index(drop=True)
        expected_career_sheet_sorted.dropna(how='all', axis=1, inplace=True)
        expected_complaint_sheet = pd.DataFrame(expected_complaints)
        expected_complaint_sheet_sorted = expected_complaint_sheet.sort_values(by=['allegation_uid']).reset_index(drop=True)
        expected_complaint_sheet_sorted.dropna(how='all', axis=1, inplace=True)
        expected_doc_sheet = pd.DataFrame([expected_document])
        expected_doc_sheet.dropna(how='all', axis=1, inplace=True)

        data_file = OfficerDatafileQuery(officer).generate_sheets_file()

        xlsx_officer_data = pd.read_excel(data_file, sheet_name=OFFICER_PROFILE_SHEET, dtype=str)
        xlsx_uof_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_SHEET, dtype=str)
        xlsx_uof_officer_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_OFFICER_SHEET)
        xlsx_uof_citizen_data = pd.read_excel(data_file, sheet_name=OFFICER_UOF_CITIZEN_SHEET)
        xlsx_incident_data = pd.read_excel(data_file, sheet_name=OFFICER_INCIDENT_SHEET)
        xlsx_incident_data_sorted = xlsx_incident_data.sort_values(by=['event_uid']).reset_index(drop=True)
        xlsx_career_data = pd.read_excel(data_file, sheet_name=OFFICER_CAREER_SHEET)
        xlsx_career_data_sorted = xlsx_career_data.sort_values(by=['event_uid']).reset_index(drop=True)
        xlsx_complaint_data = pd.read_excel(data_file, sheet_name=OFFICER_COMPLAINT_SHEET)
        xlsx_complaint_data_sorted = xlsx_complaint_data.sort_values(by=['allegation_uid']).reset_index(drop=True)
        xlsx_doc_data = pd.read_excel(data_file, sheet_name=OFFICER_DOC_SHEET, dtype=str)

        def lstrip0(row):
            row.birth_month = row.birth_month.lstrip('0')
            row.birth_day = row.birth_day.lstrip('0')
            return row

        expected_officer_sheet_strip = expected_officer_sheet.apply(lstrip0, axis='columns')

        pd.testing.assert_frame_equal(xlsx_officer_data, expected_officer_sheet_strip)
        pd.testing.assert_frame_equal(xlsx_uof_data, expected_uof_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_uof_officer_data, expected_uof_officer_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_uof_citizen_data, expected_uof_citizen_sheet, check_like=True)
        pd.testing.assert_frame_equal(xlsx_doc_data, expected_doc_sheet, check_like=True)

        pd.testing.assert_frame_equal(xlsx_incident_data_sorted, expected_incident_sheet_sorted, check_like=True,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(xlsx_career_data_sorted, expected_career_sheet_sorted, check_like=True,
                                      check_dtype=False)
        pd.testing.assert_frame_equal(xlsx_complaint_data_sorted, expected_complaint_sheet_sorted, check_like=True,
                                      check_dtype=False)
