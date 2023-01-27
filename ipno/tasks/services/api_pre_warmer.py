from django.conf import settings

import requests
from tqdm import tqdm

from departments.models import Department


class APIPreWarmer:
    def __init__(self):
        self.url = settings.SERVER_URL + "/api/"

    def pre_warm_front_page_api(self):
        summary_api = self.url + "analytics/summary/"
        front_page_card_api = self.url + "front-page-cards/"
        front_page_order_api = self.url + "front-page-orders/"
        department_list_api = self.url + "departments/"
        migratory_api = self.url + "departments/migratory/"
        officer_list_api = self.url + "officers/"
        document_list_api = self.url + "documents/"
        news_article_list_api = self.url + "news-articles/"

        front_page_apis = [
            summary_api,
            front_page_card_api,
            front_page_order_api,
            department_list_api,
            migratory_api,
            officer_list_api,
            document_list_api,
            news_article_list_api,
        ]

        error_messages = []
        for api in tqdm(front_page_apis, desc="Pre-warming front page APIs"):
            try:
                requests.get(api)
            except Exception as e:
                error_messages.append(str(e))

        return error_messages

    def pre_warm_department_api(self):
        departments = Department.objects.filter(slug__isnull=False)

        error_messages = []
        for department in tqdm(departments, desc="Pre-warming department page APIs"):
            department_detail_api = self.url + "departments/" + department.slug + "/"
            officer_api = department_detail_api + "officers/"
            document_api = department_detail_api + "documents/"
            news_article_api = department_detail_api + "news_articles/"
            dataset_api = department_detail_api + "datasets/"
            migratory_api = department_detail_api + "migratory-by-department/"

            department_apis = [
                department_detail_api,
                officer_api,
                document_api,
                news_article_api,
                dataset_api,
                migratory_api,
            ]

            for api in department_apis:
                try:
                    requests.get(api)
                except Exception as e:
                    error_messages.append(str(e))

        return error_messages
