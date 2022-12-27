DAILY_TASK = "daily_task"

TASK_TYPES = ((DAILY_TASK, "Daily task"),)

APP_TASKS = [
    {
        "task_name": "Import wrgl data",
        "command": "import_data",
        "task_type": DAILY_TASK,
    },
    {
        "task_name": "Run news articles crawlers",
        "command": "run_news_articles_crawlers",
        "task_type": DAILY_TASK,
    },
    {
        "task_name": "Run news articles' officers matching",
        "command": "run_news_articles_officers_matching",
        "task_type": DAILY_TASK,
    },
    {"task_name": "Pre-warm APIs", "command": "pre_warm_api", "task_type": DAILY_TASK},
]
