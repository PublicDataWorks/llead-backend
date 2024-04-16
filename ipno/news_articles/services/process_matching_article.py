from collections import defaultdict

from django.db.models import F, Q
from django.utils import timezone

from news_articles.models import (
    ExcludeOfficer,
    MatchedSentence,
    MatchingKeyword,
    NewsArticle,
)
from officers.models import Officer
from utils.nlp import NLP


class ProcessMatchingArticle:
    def __init__(self):
        self.start_time = timezone.now()
        self.nlp = NLP()
        self.officers = self.get_officer_data()
        self.latest_keywords_obj = MatchingKeyword.objects.order_by(
            "-created_at"
        ).first()
        self.last_run_keywords_obj = (
            MatchingKeyword.objects.filter(ran_at__isnull=False)
            .order_by("-created_at")
            .first()
        )

        self.latest_keywords = (
            set(self.latest_keywords_obj.keywords)
            if self.latest_keywords_obj
            else set()
        )
        self.last_run_keywords = (
            set(self.last_run_keywords_obj.keywords)
            if self.last_run_keywords_obj
            else set()
        )

        latest_exclude_officers = ExcludeOfficer.objects.order_by("-created_at").first()
        self.excluded_officers_ids = (
            latest_exclude_officers.officers.values_list("id", flat=True)
            if latest_exclude_officers
            else []
        )

    def process(self):
        if self.latest_keywords != self.last_run_keywords:
            self.match_processed_articles()

        self.match_unprocessed_articles()

        self.update_status()

        MatchedSentenceOfficer = MatchedSentence.officers.through
        data = (
            MatchedSentenceOfficer.objects.order_by(
                "officer_id", "matchedsentence__article__id"
            )
            .annotate(
                uid=F("officer__uid"),
                created_at=F("matchedsentence__created_at"),
                newsarticle_id=F("matchedsentence__article__id"),
            )
            .all()
        )

        count_updated_objects = data.filter(
            matchedsentence__updated_at__gte=self.start_time
        ).count()

        return count_updated_objects > 0

    def match_processed_articles(self):
        new_keywords = self.latest_keywords - self.last_run_keywords
        deleted_keywords = self.last_run_keywords - self.latest_keywords

        self.check_new_keywords(new_keywords)
        self.check_deleted_keywords(deleted_keywords)

    def match_unprocessed_articles(self):
        articles = NewsArticle.objects.filter(is_processed=False)

        self.create_news_article_matching_data(articles, self.latest_keywords)

    def check_new_keywords(self, new_keywords):
        if not new_keywords:
            return

        articles = NewsArticle.objects.filter(is_processed=True)
        self.update_news_article_matching_data(articles, new_keywords)

    def check_deleted_keywords(self, deleted_keywords):
        if not deleted_keywords:
            return

        matched_sentences = MatchedSentence.objects.filter(
            extracted_keywords__overlap=list(deleted_keywords)
        )

        for sentence in matched_sentences:
            extracted_keywords = set(sentence.extracted_keywords)
            remained_keywords = extracted_keywords - deleted_keywords
            sentence.extracted_keywords = list(remained_keywords)

            if not remained_keywords:
                sentence.delete()
            else:
                sentence.save()

    def update_news_article_matching_data(self, articles, new_keywords):
        for article in articles:
            content = article.content

            old_matched_sentence = {
                sentence.text: sentence for sentence in article.matched_sentences.all()
            }

            matched_sentences = {}

            sentences = self.nlp.extract_lines(content)
            for sentence in sentences:
                keywords = []
                for keyword in new_keywords:
                    if keyword in sentence:
                        keywords.append(keyword)
                if keywords:
                    matched_sentences[sentence] = keywords

            update_sentences = set(old_matched_sentence.keys()) & set(
                matched_sentences.keys()
            )
            create_sentences = set(matched_sentences.keys()) - set(
                old_matched_sentence.keys()
            )

            for old_sentence in update_sentences:
                matched_new_keywords = matched_sentences.get(old_sentence)

                matched_sentence = old_matched_sentence.get(old_sentence)

                old_keywords = matched_sentence.extracted_keywords.copy()
                updated_keywords = set(old_keywords) | set(matched_new_keywords)

                matched_sentence.extracted_keywords = list(updated_keywords)

                matched_sentence.save()

            for new_sentence in create_sentences:
                matched_sentence = MatchedSentence.objects.create(
                    text=new_sentence,
                    article=article,
                    extracted_keywords=matched_sentences.get(new_sentence),
                )

                matched_officers = self.nlp.process(new_sentence, self.officers)
                matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & ~Q(id__in=self.excluded_officers_ids)
                )
                exclude_matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & Q(id__in=self.excluded_officers_ids)
                )

                matched_sentence.officers.add(*matched_officers_obj)
                matched_sentence.excluded_officers.add(*exclude_matched_officers_obj)
                matched_sentence.save()

    def create_news_article_matching_data(self, articles, new_keywords):
        for article in articles:
            content = article.content

            matched_sentences = {}
            sentences = self.nlp.extract_lines(content)
            for sentence in sentences:
                keywords = []
                for keyword in new_keywords:
                    if keyword in sentence:
                        keywords.append(keyword)
                if keywords:
                    matched_sentences[sentence] = keywords

            for new_sentence in matched_sentences:
                matched_sentence = MatchedSentence.objects.create(
                    text=new_sentence,
                    article=article,
                    extracted_keywords=matched_sentences.get(new_sentence),
                )

                matched_officers = self.nlp.process(new_sentence, self.officers)
                matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & ~Q(id__in=self.excluded_officers_ids)
                )
                exclude_matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & Q(id__in=self.excluded_officers_ids)
                )

                matched_sentence.officers.add(*matched_officers_obj)
                matched_sentence.excluded_officers.add(*exclude_matched_officers_obj)
                matched_sentence.save()

            article.is_processed = True
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
