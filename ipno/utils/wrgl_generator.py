from io import BytesIO as IO

import pandas as pd
from django.conf import settings
from wrgl import Repository


class WrglGenerator:
    def create_wrgl_commit(self, repo_name, message, csv_pks, csv_file, branch='main'):
        repo = Repository(
            f'https://hub.wrgl.co/api/users/{settings.WRGL_USER}/repos/{repo_name}/',
            settings.WRGL_API_KEY
        )

        result = repo.commit(
            branch=branch,
            message=message,
            file=IO(csv_file),
            primary_key=csv_pks,
        )

        return result

    def generate_csv_file(self, objects, columns):
        csv_file = IO()
        dataframe = pd.DataFrame(objects.values(*columns))
        dataframe.to_csv(csv_file, index=False)

        csv_value = csv_file.getvalue()
        csv_file.close()

        return csv_value
