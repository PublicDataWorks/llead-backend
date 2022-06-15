OFFICERS_LIMIT = 20

JOINED_TIMELINE_KIND = 'JOINED'
LEFT_TIMELINE_KIND = 'LEFT'
COMPLAINT_TIMELINE_KIND = 'COMPLAINT'
UOF_TIMELINE_KIND = 'UOF'
APPEAL_TIMELINE_KIND = 'APPEAL'
DOCUMENT_TIMELINE_KIND = 'DOCUMENT'
NEWS_ARTICLE_TIMELINE_KIND = 'NEWS_ARTICLE'
SALARY_CHANGE_TIMELINE_KIND = 'SALARY_CHANGE'
RANK_CHANGE_TIMELINE_KIND = 'RANK_CHANGE'
UNIT_CHANGE_TIMELINE_KIND = 'UNIT_CHANGE'

OFFICER_LEVEL_1_CERT = "officer_level_1_cert"
OFFICER_PC_12_QUALIFICATION = "officer_pc_12_qualification"
OFFICER_RANK = "officer_rank"
OFFICER_DEPT = "officer_dept"
OFFICER_HIRE = "officer_hire"
OFFICER_LEFT = "officer_left"
OFFICER_PAY_PROG_START = "officer_pay_prog_start"
OFFICER_PAY_EFFECTIVE = "officer_pay_effective"

COMPLAINT_INCIDENT = "complaint_incident"
COMPLAINT_RECEIVE = "complaint_receive"
ALLEGATION_CREATE = "allegation_create"
INVESTIGATION_COMPLETE = "investigation_complete"
SUSPENSION_START = "suspension_start"
SUSPENSION_END = "suspension_end"
COMPLAINT_ALL_EVENTS = [
    COMPLAINT_INCIDENT,
    COMPLAINT_RECEIVE,
    ALLEGATION_CREATE,
    INVESTIGATION_COMPLETE,
    SUSPENSION_START,
    SUSPENSION_END,
]

APPEAL_FILE = "appeal_file"
APPEAL_HEARING = "appeal_hearing"
APPEAL_RENDER = "appeal_render"

UOF_INCIDENT = "uof_incident"
UOF_RECEIVE = "uof_receive"
UOF_ASSIGNED = "uof_assigned"
UOF_COMPLETED = "uof_completed"
UOF_CREATED = "uof_created"
UOF_DUE = "uof_due"
UOF_OCCUR = "uof_occur"
UOF_ALL_EVENTS = [
    UOF_INCIDENT,
    UOF_RECEIVE,
    UOF_ASSIGNED,
    UOF_COMPLETED,
    UOF_CREATED,
    UOF_DUE,
    UOF_OCCUR,
]

AWARD_RECEIVE = "award_receive"

OFFICER_PROFILE_SHEET = 'Demographic profile'
OFFICER_INCIDENT_SHEET = 'Incidents'
OFFICER_COMPLAINT_SHEET = 'Complaint details'
OFFICER_UOF_SHEET = 'Use of force details'
OFFICER_UOF_OFFICER_SHEET = 'Use of force officer details'
OFFICER_UOF_CITIZEN_SHEET = 'Use of force citizen details'
OFFICER_CAREER_SHEET = 'Career history'
OFFICER_DOC_SHEET = 'Documents'

OFFICER_PROFILE_FIELDS = [
            'uid', 'last_name', 'middle_name',
            'first_name', 'birth_year', 'birth_month', 'birth_day', 'race',
            'sex'
]

OFFICER_DOC_FIELDS = [
            'docid', 'day', 'month', 'year',
            'url', 'title',
]

OFFICER_INCIDENT_FIELDS = [
    'event_uid', 'kind', 'year', 'month', 'agency', 'uid', 'uof_uid',
    'day', 'time', 'raw_date', 'allegation_uid', 'appeal_uid',
    'badge_no', 'employee_id', 'department_code', 'department_desc',
    'division_desc', 'sub_division_a_desc', 'sub_division_b_desc',
    'current_supervisor', 'employee_class', 'rank_code', 'rank_desc',
    'sworn', 'officer_inactive', 'employee_type', 'years_employed',
    'salary', 'salary_freq', 'award', 'award_comments', 'left_reason',
]

OFFICER_COMPLAINT_FIELDS = [
    'allegation_uid', 'tracking_id', 'uid', 'case_number', 'allegation',
    'investigation_status', 'assigned_department', 'assigned_division',
    'traffic_stop', 'body_worn_camera_available', 'app_used',
    'citizen_arrested', 'citizen', 'disposition', 'complainant_name',
    'complainant_type', 'complainant_sex', 'complainant_race', 'action',
    'initial_action', 'incident_type', 'supervisor_uid', 'supervisor_rank',
    'badge_no', 'department_code', 'department_desc', 'employment_status',
    'investigator', 'investigator_uid', 'investigator_rank', 'shift_supervisor',
    'allegation_desc', 'investigating_department', 'referred_by', 'incident_location',
    'disposition_desc', 'agency',
]

OFFICER_UOF_FIELDS = [
    'uof_uid', 'tracking_id', 'investigation_status',
    'service_type', 'light_condition', 'weather_condition', 'shift_time',
    'disposition', 'division', 'division_level', 'unit', 'originating_bureau',
    'agency', 'use_of_force_reason',
]

OFFICER_UOF_OFFICER_FIELDS = [
    'uof_uid', 'uid', 'use_of_force_description', 'use_of_force_level', 'use_of_force_effective',
    'age', 'years_of_service', 'officer_injured',
]

OFFICER_UOF_CITIZEN_FIELDS = [
    'uof_citizen_uid', 'uof_uid', 'citizen_influencing_factors', 'citizen_distance_from_officer',
    'citizen_arrested', 'citizen_arrest_charges', 'citizen_hospitalized', 'citizen_injured',
    'citizen_age', 'citizen_race', 'citizen_sex',
]

TIMELINE_EVENT_KINDS = [
    COMPLAINT_RECEIVE,
    UOF_RECEIVE,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    OFFICER_DEPT,
]

OFFICER_CAREER_KINDS = [
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    OFFICER_DEPT,
]

EVENT_KINDS = (
    (OFFICER_LEVEL_1_CERT, OFFICER_LEVEL_1_CERT),
    (OFFICER_PC_12_QUALIFICATION, OFFICER_PC_12_QUALIFICATION),
    (OFFICER_RANK, OFFICER_RANK),
    (OFFICER_DEPT, OFFICER_DEPT),
    (OFFICER_HIRE, OFFICER_HIRE),
    (OFFICER_LEFT, OFFICER_LEFT),
    (OFFICER_PAY_PROG_START, OFFICER_PAY_PROG_START),
    (OFFICER_PAY_EFFECTIVE, OFFICER_PAY_EFFECTIVE),
    (COMPLAINT_INCIDENT, COMPLAINT_INCIDENT),
    (COMPLAINT_RECEIVE, COMPLAINT_RECEIVE),
    (ALLEGATION_CREATE, ALLEGATION_CREATE),
    (INVESTIGATION_COMPLETE, INVESTIGATION_COMPLETE),
    (SUSPENSION_START, SUSPENSION_START),
    (SUSPENSION_END, SUSPENSION_END),
    (APPEAL_FILE, APPEAL_FILE),
    (APPEAL_HEARING, APPEAL_HEARING),
    (APPEAL_RENDER, APPEAL_RENDER),
    (UOF_INCIDENT, UOF_INCIDENT),
    (UOF_RECEIVE, UOF_RECEIVE),
    (UOF_ASSIGNED, UOF_ASSIGNED),
    (UOF_COMPLETED, UOF_COMPLETED),
    (UOF_CREATED, UOF_CREATED),
    (UOF_DUE, UOF_DUE),
    (AWARD_RECEIVE, AWARD_RECEIVE),
)
