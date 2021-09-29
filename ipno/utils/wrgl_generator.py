import requests
from io import BytesIO as IO

import pandas as pd
from django.conf import settings


class WrglGenerator:
    def create_wrgl_commit(self, repo_name, message, csv_pks, csv_file):
        url = f'https://www.wrgl.co/api/v1/users/{settings.WRGL_USER}/repos'

        data = {
            'repoName': repo_name,
            'message': message,
            'csv.primaryKey': csv_pks,
        }

        header = {
            'Authorization': f'APIKEY {settings.WRGL_API_KEY}',
        }

        response = requests.post(url, data=data, headers=header, files={'csv.dataFile': csv_file})

        return response

    def generate_csv_file(self, objects, columns):
        csv_file = IO()
        dataframe = pd.DataFrame(objects.values(*columns))
        dataframe.to_csv(csv_file,
                         index=False,
                         compression="gzip")

        csv_value = csv_file.getvalue()
        csv_file.close()

        return csv_value
