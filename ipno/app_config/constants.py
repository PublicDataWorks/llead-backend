APP_CONFIG = [
    {
        "name": "NO_OF_RECENT_SEARCHES",
        "value": "5",
        "description": "Number of recent searches",
    },
    {
        "name": "ANALYTIC_RECENT_DAYS",
        "value": "30",
        "description": "Number of analytic recent days",
    },
    {
        "name": "NEWS_ARTICLE_THRESHOLD",
        "value": "0.5",
        "description": "The threshold for news article classification",
    },
]

APP_TEXT_CONTENTS = [
    {
        "name": "ABOUT_PAGE_SUMMARY",
        "value": "LLEAD introduction",
        "description": "The summary text display in about.",
    },
    {
        "name": "FOOTER_TEXT",
        "value": (
            "[**Innocence Project New Orleans**](https://ip-no.org) in collaboration"
            " with [**Public Data Works**](https://publicdata.works)"
        ),
        "description": "The footer text display in every page.",
    },
    {
        "name": "FORGOT_PASSWORD_EMAIL",
        "value": (
            "Here is the [link]({HOST}/reset-password/{reset_password_token}) to reset"
            " your password."
        ),
        "description": "The forgot password email content.",
    },
]

CMS_KEY = "CMS"

DEPARTMENT = "DEPARTMENT"
OFFICER = "OFFICER"
DOCUMENT = "DOCUMENT"
NEWS_ARTICLE = "NEWS_ARTICLE"

APP_FRONT_PAGE_SECTIONS = [
    DEPARTMENT,
    OFFICER,
    NEWS_ARTICLE,
    DOCUMENT,
]

FRONT_PAGE_INTRODUCTION_CARDS = [
    {
        "order": 1,
        "content": (
            "LLEAD is the Louisiana Law Enforcement Accountability Database. LLEAD"
            " consolidates data from over 600 law enforcement agencies in the state of"
            " Louisiana. Over 400 officers that have moved between law enforcement"
            " agencies across the state in the years xxxx-xxxx. Officers transfer for a"
            " variety of reasons and are required by law to disclose their reason for"
            " changing employers. Our data indicate that x% involuntary resigned due to"
            " termination or while under investigation — x% were terminated, x%"
            " voluntarily resigned, and x% resigned. x% did not disclose their reason"
            " for changing employers."
        ),
    },
    {
        "order": 2,
        "content": (
            "# officers transferred to a new agency after being fired for misconduct or"
            " resigning while under investigation for misconduct.  12% of these"
            " officers were fired prior to transfer. 15% resigned and transferred while"
            " under investigation for misconduct. LLEAD contains data detailing 1152"
            " allegations from 26 law enforcement agencies for 2020. Of these 1152"
            " allegations, 18% were sustained after investigation. The 26 law"
            " enforcement agencies included in this figure police 45% of Louisiana’s"
            " population."
        ),
    },
    {
        "order": 3,
        "content": "",
    },
]

DEFAULT_RECENT_DAYS = 30
