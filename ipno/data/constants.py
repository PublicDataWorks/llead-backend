WRGL_USER = 'ipno'

OFFICER_MODEL_NAME = 'Officer'
EVENT_MODEL_NAME = 'Event'
COMPLAINT_MODEL_NAME = 'Complaint'
USE_OF_FORCE_MODEL_NAME = 'UseOfForce'
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
        'repo_name': 'complaint',
        'data_model': COMPLAINT_MODEL_NAME,
    },
    {
        'repo_name': 'use-of-force',
        'data_model': USE_OF_FORCE_MODEL_NAME,
    },
]

IMPORT_LOG_STATUS_STARTED = 'started'
IMPORT_LOG_STATUS_NO_NEW_COMMIT = 'no_new_commit'
IMPORT_LOG_STATUS_RUNNING = 'running'
IMPORT_LOG_STATUS_FINISHED = 'finished'
IMPORT_LOG_STATUS_ERROR = 'error'

IMPORT_LOG_STATUSES = (
    (IMPORT_LOG_STATUS_STARTED, 'Started'),
    (IMPORT_LOG_STATUS_NO_NEW_COMMIT, 'No new commit'),
    (IMPORT_LOG_STATUS_RUNNING, 'Running'),
    (IMPORT_LOG_STATUS_FINISHED, 'Finished'),
    (IMPORT_LOG_STATUS_ERROR, 'Error')
)
