from io import BytesIO as IO

from django.conf import settings

import pandas as pd
from wrgl import Repository


class WrglGenerator:
    def create_wrgl_commit(self, message, csv_pks, csv_file, branch):
        repo = Repository(
            "https://wrgl.llead.co/",
            settings.WRGL_CLIENT_ID,
            settings.WRGL_CLIENT_SECRET,
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
