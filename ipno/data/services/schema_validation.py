from django.conf import settings

import pandas as pd

from utils.models import APITemplateModel
from utils.slack_notification import notify_slack


class SchemaValidation:
    def __init__(self):
        self.models = APITemplateModel.__subclasses__()
        self.model_schemas = self._get_schemas()

    def _get_schemas(self) -> dict:
        model_schemas = {}

        for model in self.models:
            fields = model._meta.fields
            base_fields = getattr(model, "BASE_FIELDS", set())
            custom_fields = getattr(model, "CUSTOM_FIELDS", set())
            excluding_fields = base_fields | custom_fields

            fixed_fields = {field.name for field in fields} - excluding_fields

            model_schemas[model._meta.model_name] = fixed_fields

        return model_schemas

    def _check_fields(self, csv_file_path, fixed_fields) -> tuple:
        checking_fields = set(pd.read_csv(csv_file_path, nrows=1).columns)
        missing_fixed_fields = fixed_fields - checking_fields
        unused_fields = checking_fields - fixed_fields

        return missing_fixed_fields, unused_fields

    def validate_schemas(self, data_location_mapping):
        err_msgs, unused_msgs = [], []

        for model in self.models:
            model_name = model._meta.model_name
            fixed_fields = self.model_schemas[model_name]
            csv_file_path = data_location_mapping[model_name]
            missing_fixed_fields, unused_fields = self._check_fields(
                csv_file_path, fixed_fields
            )

            if missing_fixed_fields:
                err_msgs.extend(
                    f">- Missing required fields in table `{model_name}`: "
                    f"*{' | '.join(missing_fixed_fields)}*\n"
                )

            if unused_fields:
                unused_msgs.extend(
                    f">- Unused fields in table `{model_name}`:"
                    f" {' | '.join(unused_fields)}\n"
                )

        message = (
            "====================\nResult after schema validation in"
            f" *`{settings.ENVIRONMENT.upper()}`* environment,\n\n"
        )

        if err_msgs:
            message += "*ERROR happened*\n\n"
            message += "".join(err_msgs)
        else:
            message += "*Required fields are validated successfully!*\n\n"

        if unused_msgs:
            message += "\n_*(Warning) Unused fields:*_\n\n"
            message += "".join(unused_msgs)

        notify_slack(message)

        return not err_msgs
