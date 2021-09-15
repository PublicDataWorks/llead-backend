APP_CONFIG = [
    {
        'name': 'NO_OF_RECENT_SEARCHES',
        'value': '5',
        'description': 'Number of recent searches'
    },
    {
        'name': 'ANALYTIC_RECENT_DAYS',
        'value': '30',
        'description': 'Number of analytic recent days'
    }
]

APP_TEXT_CONTENTS = [
    {
        'name': 'FRONT_PAGE_SUMMARY',
        'value': 'We are building a database of **Louisiana** police officers, departments, and documents.',
        'description': 'The summary text display in frontpage.'
    },
    {
        'name': 'FOOTER_TEXT',
        'value': '[**Innocence Project New Orleans**](https://ip-no.org) in collaboration with [**Public Data Works**]'
                 '(https://publicdata.works)',
        'description': 'The footer text display in every page.'
    },
    {
        'name': 'FORGOT_PASSWORD_EMAIL',
        'value': 'Here is the [link]({HOST}/reset-password/{reset_password_token}) to reset your '
                 'password.',
        'description': 'The forgot password email content.'
    }
]

CMS_KEY = 'CMS'

DEPARTMENT = 'DEPARTMENT'
OFFICER = 'OFFICER'
DOCUMENT = 'DOCUMENT'
NEWS_ARTICLE = 'NEWS_ARTICLE'

APP_FRONT_PAGE_SECTIONS = [
    DEPARTMENT,
    OFFICER,
    NEWS_ARTICLE,
    DOCUMENT,
]
