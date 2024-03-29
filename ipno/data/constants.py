OFFICER_MODEL_NAME = "Officer"
AGENCY_MODEL_NAME = "Department"
EVENT_MODEL_NAME = "Event"
COMPLAINT_MODEL_NAME = "Complaint"
USE_OF_FORCE_MODEL_NAME = "UseOfForce"
USE_OF_FORCE_OFFICER_MODEL_NAME = "UseOfForceOfficer"
CITIZEN_MODEL_NAME = "Citizen"
APPEAL_MODEL_NAME = "Appeal"
DOCUMENT_MODEL_NAME = "Document"
NEWS_ARTICLE_MODEL_NAME = "NewsArticle"
NEWS_ARTICLE_OFFICER_MODEL_NAME = "NewsArticleOfficer"
NEWS_ARTICLE_CLASSIFICATION_MODEL_NAME = "NewsArticleClassification"
PERSON_MODEL_NAME = "Person"
BRADY_MODEL_NAME = "Brady"
POST_OFFICE_HISTORY_MODEL_NAME = "PostOfficeHistory"
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
