OFFICERS_LIMIT = 20

JOINED_TIMELINE_KIND = "JOINED"
LEFT_TIMELINE_KIND = "LEFT"
TERMINATED_TIMELINE_KIND = "TERMINATED"
RESIGNED_TIMELINE_KIND = "RESIGNED"
COMPLAINT_TIMELINE_KIND = "COMPLAINT"
UOF_TIMELINE_KIND = "UOF"
APPEAL_TIMELINE_KIND = "APPEAL"
DOCUMENT_TIMELINE_KIND = "DOCUMENT"
NEWS_ARTICLE_TIMELINE_KIND = "NEWS_ARTICLE"
SALARY_CHANGE_TIMELINE_KIND = "SALARY_CHANGE"
RANK_CHANGE_TIMELINE_KIND = "RANK_CHANGE"
UNIT_CHANGE_TIMELINE_KIND = "UNIT_CHANGE"
FIREARM_CERTIFICATION_TIMELINE_KIND = "FIREARM_CERTIFICATION"
PC_12_QUALIFICATION_TIMELINE_KIND = "PC_12_QUALIFICATION"
BRADY_LIST_TIMELINE_KIND = "BRADY_LIST"
POST_DECERTIFICATION_TIMELINE_KIND = "POST_DECERTIFICATION"

OFFICER_LEVEL_1_CERT = "officer_level_1_cert"
OFFICER_PC_12_QUALIFICATION = "officer_pc_12_qualification"
OFFICER_POST_DECERTIFICATION = "officer_post_decertification"
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
BRADY_LIST = "brady_list"

OFFICER_PROFILE_SHEET = "Demographic profile"
OFFICER_INCIDENT_SHEET = "Incidents"
OFFICER_COMPLAINT_SHEET = "Complaint details"
OFFICER_UOF_SHEET = "Use of force details"
OFFICER_CITIZEN_SHEET = "Citizen details"
OFFICER_CAREER_SHEET = "Career history"
OFFICER_DOC_SHEET = "Documents"

OFFICER_PROFILE_FIELDS = [
    "uid",
    "last_name",
    "middle_name",
    "first_name",
    "birth_year",
    "birth_month",
    "birth_day",
    "race",
    "sex",
]

OFFICER_DOC_FIELDS = [
    "docid",
    "day",
    "month",
    "year",
    "url",
    "title",
]

OFFICER_INCIDENT_FIELDS = [
    "event_uid",
    "kind",
    "year",
    "month",
    "agency",
    "uid",
    "uof_uid",
    "day",
    "time",
    "raw_date",
    "allegation_uid",
    "appeal_uid",
    "badge_no",
    "department_code",
    "department_desc",
    "rank_code",
    "rank_desc",
    "salary",
    "salary_freq",
    "left_reason",
]

OFFICER_COMPLAINT_FIELDS = [
    "allegation_uid",
    "tracking_id",
    "uid",
    "allegation",
    "disposition",
    "action",
    "allegation_desc",
    "agency",
]

OFFICER_UOF_FIELDS = [
    "uof_uid",
    "uid",
    "tracking_id",
    "service_type",
    "disposition",
    "use_of_force_description",
    "officer_injured",
    "agency",
    "use_of_force_reason",
]

OFFICER_CITIZEN_FIELDS = [
    "citizen_uid",
    "allegation_uid",
    "uof_uid",
    "citizen_arrested",
    "citizen_hospitalized",
    "citizen_injured",
    "citizen_age",
    "citizen_race",
    "citizen_sex",
    "agency",
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

EVENT_KINDS = [
    OFFICER_LEVEL_1_CERT,
    OFFICER_PC_12_QUALIFICATION,
    OFFICER_RANK,
    OFFICER_DEPT,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_PROG_START,
    OFFICER_PAY_EFFECTIVE,
    COMPLAINT_INCIDENT,
    COMPLAINT_RECEIVE,
    ALLEGATION_CREATE,
    INVESTIGATION_COMPLETE,
    SUSPENSION_START,
    SUSPENSION_END,
    APPEAL_FILE,
    APPEAL_HEARING,
    APPEAL_RENDER,
    UOF_INCIDENT,
    UOF_RECEIVE,
    UOF_ASSIGNED,
    UOF_COMPLETED,
    UOF_CREATED,
    UOF_DUE,
    AWARD_RECEIVE,
    BRADY_LIST,
]
