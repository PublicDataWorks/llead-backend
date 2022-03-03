WRGL_USER = 'ipno'

OFFICER_MODEL_NAME = 'Officer'
EVENT_MODEL_NAME = 'Event'
COMPLAINT_MODEL_NAME = 'Complaint'
USE_OF_FORCE_MODEL_NAME = 'UseOfForce'
APPEAL_MODEL_NAME = 'Appeal'
DOCUMENT_MODEL_NAME = 'Document'
NEWS_ARTICLE_MODEL_NAME = 'NewsArticle'
NEWS_ARTICLE_OFFICER_MODEL_NAME = 'NewsArticleOfficer'
PERSON_MODEL_NAME = 'Person'
WRGL_REPOS_DEFAULT = [
    {
        'repo_name': 'personnel',
        'data_model': OFFICER_MODEL_NAME,
    },
    {
        'repo_name': 'event',
        'data_model': EVENT_MODEL_NAME,
    },
    {
        'repo_name': 'allegation',
        'data_model': COMPLAINT_MODEL_NAME,
    },
    {
        'repo_name': 'use-of-force',
        'data_model': USE_OF_FORCE_MODEL_NAME,
    },
    {
        'repo_name': 'documents',
        'data_model': DOCUMENT_MODEL_NAME,
    },
    {
        'repo_name': 'news_articles',
        'data_model': NEWS_ARTICLE_MODEL_NAME,
    },
    {
        'repo_name': 'news_articles_officers',
        'data_model': NEWS_ARTICLE_OFFICER_MODEL_NAME,
    },
    {
        'repo_name': 'person',
        'data_model': PERSON_MODEL_NAME,
    },
    {
        'repo_name': 'appeal-hearing',
        'data_model': APPEAL_MODEL_NAME,
    },
]

IMPORT_LOG_STATUS_STARTED = 'started'
IMPORT_LOG_STATUS_NO_NEW_COMMIT = 'no_new_commit'
IMPORT_LOG_STATUS_NO_NEW_DATA = 'no_new_data'
IMPORT_LOG_STATUS_RUNNING = 'running'
IMPORT_LOG_STATUS_FINISHED = 'finished'
IMPORT_LOG_STATUS_ERROR = 'error'

IMPORT_LOG_STATUSES = (
    (IMPORT_LOG_STATUS_STARTED, 'Started'),
    (IMPORT_LOG_STATUS_NO_NEW_COMMIT, 'No new commit'),
    (IMPORT_LOG_STATUS_NO_NEW_DATA, 'No new data'),
    (IMPORT_LOG_STATUS_RUNNING, 'Running'),
    (IMPORT_LOG_STATUS_FINISHED, 'Finished'),
    (IMPORT_LOG_STATUS_ERROR, 'Error')
)
