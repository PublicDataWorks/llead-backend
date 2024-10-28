HOURLY_TASK = "hourly_task"
DAILY_TASK = "daily_task"

TASK_TYPES = (
    (HOURLY_TASK, "Hourly task"),
    (DAILY_TASK, "Daily task"),
)

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
        "task_name": "Submit news articles for LLM analysis",
        "command": "submit_llm_analysis",
        "task_type": HOURLY_TASK,  # Submit new articles frequently
    },
    {
        "task_name": "Process completed LLM analysis batches",
        "command": "process_llm_batches",
        "task_type": DAILY_TASK,  # Process results once per day
    },
    {
        "task_name": "Run news articles' officers matching",
        "command": "run_news_articles_officers_matching",
        "task_type": DAILY_TASK,
    },
    {"task_name": "Pre-warm APIs", "command": "pre_warm_api", "task_type": DAILY_TASK},
]
