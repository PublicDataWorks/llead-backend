from django.conf import settings

import requests

from data.models import WrglRepo
from utils.models import APITemplateModel
from utils.slack_notification import notify_slack

SCHEMA_MAPPING = {
    "agency-reference-list": "department",
    "allegation": "complaint",
    "appeal-hearing": "appeal",
    "documents": "document",
    "event": "event",
    "personnel": "officer",
    "person": "person",
    "use-of-force": "useofforce",
    "citizens": "citizen",
    "brady": "brady",
    "news_article_classification": "newsarticleclassification",
    "post-officer-history": "postofficerhistory",
}


def get_schemas():
    models = APITemplateModel.__subclasses__()
    model_schemas = {}
    choice_fields = {}

    for model in models:
        model_name = model._meta.model_name
        fields = model._meta.fields
        base_fields = getattr(model, "BASE_FIELDS", set())
        custom_fields = getattr(model, "CUSTOM_FIELDS", set())
        excluding_fields = base_fields | custom_fields
        fixed_fields = []

        for field in fields:
            field_name = field.name
            if field.name not in excluding_fields:
                fixed_fields.append(field_name)

            if field.choices:
                choice_fields[field_name] = (choice[0] for choice in field.choices)

        model_schemas[model_name] = fixed_fields

    return model_schemas, choice_fields


def check_fields(schema_name, fixed_fields):
    wrgl_response = requests.get(
        f"https://wrgl.llead.co/refs/heads/{schema_name}/"
    ).json()
    checking_fields = set(wrgl_response["table"]["columns"])
    commit_hash = wrgl_response["sum"]

    missing_fixed_fields = fixed_fields - checking_fields
    unused_fields = checking_fields - fixed_fields

    return commit_hash, missing_fixed_fields, unused_fields


def validate_schemas():
    schemas = get_schemas()[0]
    latest_commit_hashes = {}
    message = (
        "====================\nResult after schema validation in"
        f" *`{settings.ENVIRONMENT.upper()}`* environment,\n\n"
    )
    err_msgs, unused_msgs = [], []

    for wrgl_repo, model in SCHEMA_MAPPING.items():
        fixed_fields = set(schemas[model])
        commit_hash, missing_fixed_fields, unused_fields = check_fields(
            wrgl_repo, fixed_fields
        )

        if missing_fixed_fields:
            err_msgs.extend(
                f">- Missing required fields in table `{wrgl_repo}`: "
                f"*{' | '.join(missing_fixed_fields)}*\n"
            )

        if unused_fields:
            unused_msgs.extend(
                f">- Unused fields in table `{wrgl_repo}`:"
                f" {' | '.join(unused_fields)}\n"
            )

        latest_commit_hashes[wrgl_repo] = commit_hash

    if err_msgs:
        message += "*ERROR happened*\n\n"
        message += "".join(err_msgs)
    else:
        message += "*Required fields are validated successfully!*\n\n"
        repos = WrglRepo.objects.filter(repo_name__in=SCHEMA_MAPPING)
        for repo in repos:
            repo.latest_commit_hash = latest_commit_hashes[repo.repo_name]

        WrglRepo.objects.bulk_update(repos, ["latest_commit_hash"])

    if unused_msgs:
        message += "\n_*(Warning) Unused fields:*_\n\n"
        message += "".join(unused_msgs)

    notify_slack(message)

    return not err_msgs
