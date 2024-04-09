OFFICER_MODEL_NAME = "officer"
AGENCY_MODEL_NAME = "department"
EVENT_MODEL_NAME = "event"
COMPLAINT_MODEL_NAME = "complaint"
USE_OF_FORCE_MODEL_NAME = "useofforce"
USE_OF_FORCE_OFFICER_MODEL_NAME = "useofforceofficer"
CITIZEN_MODEL_NAME = "citizen"
APPEAL_MODEL_NAME = "appeal"
DOCUMENT_MODEL_NAME = "document"
NEWS_ARTICLE_MODEL_NAME = "newsarticle"
NEWS_ARTICLE_OFFICER_MODEL_NAME = "newsarticleofficer"
NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME = "newsarticleclassification"
PERSON_MODEL_NAME = "person"
BRADY_MODEL_NAME = "brady"
POST_OFFICE_HISTORY_MODEL_NAME = "postofficerhistory"
WRGL_REPOS_DEFAULT = [
    {
        "repo_name": "agency-reference-list",
        "data_model": AGENCY_MODEL_NAME,
    },
    {
        "repo_name": "personnel",
        "data_model": OFFICER_MODEL_NAME,
    },
    {
        "repo_name": "event",
        "data_model": EVENT_MODEL_NAME,
    },
    {
        "repo_name": "allegation",
        "data_model": COMPLAINT_MODEL_NAME,
    },
    {
        "repo_name": "use-of-force",
        "data_model": USE_OF_FORCE_MODEL_NAME,
    },
    {
        "repo_name": "citizens",
        "data_model": CITIZEN_MODEL_NAME,
    },
    {
        "repo_name": "documents",
        "data_model": DOCUMENT_MODEL_NAME,
    },
    {
        "repo_name": "news_articles",
        "data_model": NEWS_ARTICLE_MODEL_NAME,
    },
    {
        "repo_name": "news_articles_officers",
        "data_model": NEWS_ARTICLE_OFFICER_MODEL_NAME,
    },
    {
        "repo_name": "person",
        "data_model": PERSON_MODEL_NAME,
    },
    {
        "repo_name": "appeal-hearing",
        "data_model": APPEAL_MODEL_NAME,
    },
    {
        "repo_name": "brady",
        "data_model": BRADY_MODEL_NAME,
    },
    {
        "repo_name": "news_article_classification",
        "data_model": NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME,
    },
    {
        "repo_name": "post-officer-history",
        "data_model": POST_OFFICE_HISTORY_MODEL_NAME,
    },
]

IMPORT_LOG_STATUS_STARTED = "started"
IMPORT_LOG_STATUS_NO_NEW_COMMIT = "no_new_commit"
IMPORT_LOG_STATUS_NO_NEW_DATA = "no_new_data"
IMPORT_LOG_STATUS_RUNNING = "running"
IMPORT_LOG_STATUS_FINISHED = "finished"
IMPORT_LOG_STATUS_ERROR = "error"

IMPORT_LOG_STATUSES = (
    (IMPORT_LOG_STATUS_STARTED, "Started"),
    (IMPORT_LOG_STATUS_NO_NEW_COMMIT, "No new commit"),
    (IMPORT_LOG_STATUS_NO_NEW_DATA, "No new data"),
    (IMPORT_LOG_STATUS_RUNNING, "Running"),
    (IMPORT_LOG_STATUS_FINISHED, "Finished"),
    (IMPORT_LOG_STATUS_ERROR, "Error"),
)

MAP_IMAGES_SUB_DIR = "map_images"
