from collections import defaultdict

from django.conf import settings
from django.db.models import F, Q
from django.utils import timezone

from data.constants import NEWS_ARTICLE_OFFICER_MODEL_NAME
from data.models import WrglRepo
from news_articles.constants import NEWS_ARTICLE_OFFICER_WRGL_COLUMNS
from news_articles.models import MatchingKeyword, NewsArticle, ExcludeOfficer
from officers.models import Officer
from utils.nlp import NLP
from utils.wrgl_generator import WrglGenerator


class ProcessMatchingArticle:
    def __init__(self):
        self.start_time = timezone.now()
        self.nlp = NLP()
        self.wrgl = WrglGenerator()
        self.officers = self.get_officer_data()
        self.latest_keywords_obj = MatchingKeyword.objects.order_by('-created_at').first()
        self.last_run_keywords_obj = MatchingKeyword.objects.filter(ran_at__isnull=False).order_by('-created_at').first()

        self.latest_keywords = set(self.latest_keywords_obj.keywords) if self.latest_keywords_obj else set()
        self.last_run_keywords = set(self.last_run_keywords_obj.keywords) if self.last_run_keywords_obj else set()

        latest_exclude_officers = ExcludeOfficer.objects.order_by('-created_at').first()
        self.excluded_officers_ids = latest_exclude_officers.officers.values_list(
            'id',
            flat=True
        ) if latest_exclude_officers else []

    def process(self):
        if self.latest_keywords != self.last_run_keywords:
            self.match_processed_articles()

        self.match_unprocessed_articles()

        self.update_status()
        return self.commit_data_to_wrgl()

    def match_processed_articles(self):
        new_keywords = self.latest_keywords - self.last_run_keywords
        deleted_keywords = self.last_run_keywords - self.latest_keywords

        self.check_new_keywords(new_keywords)
        self.check_deleted_keywords(deleted_keywords)

    def match_unprocessed_articles(self):
        articles = NewsArticle.objects.filter(extracted_keywords__isnull=True)
        for article in articles:
            article.extracted_keywords = []

        self.update_news_article_matching_data(articles, self.latest_keywords)

    def check_new_keywords(self, new_keywords):
        articles = NewsArticle.objects.filter(extracted_keywords__isnull=False)

        self.update_news_article_matching_data(articles, new_keywords)

    def check_deleted_keywords(self, deleted_keywords):
        articles = NewsArticle.objects.filter(extracted_keywords__len__gt=0)

        for article in articles:
            extracted_keywords = set(article.extracted_keywords)
            remained_keywords = extracted_keywords - deleted_keywords
            article.extracted_keywords = list(remained_keywords)

            if not remained_keywords:
                article.officers.clear()
                article.excluded_officers.clear()

            article.save()

    def update_news_article_matching_data(self, articles, new_keywords):
        for article in articles:
            old_keywords = article.extracted_keywords
            keywords = old_keywords.copy()

            keywords.extend([keyword for keyword in new_keywords if keyword in article.content])

            if keywords and not old_keywords:
                matched_officers = self.nlp.process(article.content, self.officers)

                matched_officers_obj = Officer.objects.filter(Q(id__in=matched_officers) & ~Q(id__in=self.excluded_officers_ids))
                exclude_matched_officers_obj = Officer.objects.filter(Q(id__in=matched_officers) & Q(id__in=self.excluded_officers_ids))

                article.officers.add(*matched_officers_obj)
                article.excluded_officers.add(*exclude_matched_officers_obj)

            article.extracted_keywords = keywords
            article.save()

    def get_officer_data(self):
        officers = Officer.objects.all()
        officers_data = defaultdict(list)

        for officer in officers:
            officers_data[officer.name].append(officer.id)

        return officers_data

    def update_status(self):
        if self.latest_keywords_obj:
            self.latest_keywords_obj.ran_at = timezone.now()
            self.latest_keywords_obj.save()

    def commit_data_to_wrgl(self):
        NewsArticleOfficer = NewsArticle.officers.through
        data = NewsArticleOfficer.objects.annotate(
                    uid=F('officer__uid'),
                    created_at=F('newsarticle__created_at')
                ).all()

        count_updated_objects = data.filter(newsarticle__updated_at__gte=self.start_time).count()

        if count_updated_objects:
            columns = NEWS_ARTICLE_OFFICER_WRGL_COLUMNS
            gzexcel = self.wrgl.generate_csv_file(data, columns)

            response = self.wrgl.create_wrgl_commit(
                settings.NEWS_ARTICLE_OFFICER_WRGL_REPO,
                f'+ {len(self.latest_keywords)} keyword(s)',
                'id',
                gzexcel
            )

            commit_hash = response.json()['hash']
            wrgl_repo = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

            if commit_hash and wrgl_repo.commit_hash != commit_hash:
                wrgl_repo.commit_hash = commit_hash
                wrgl_repo.save()

        return count_updated_objects > 0
