from unittest.mock import Mock, patch

from django.test import TestCase

from news_articles.factories import (
    ExcludeOfficerFactory,
    MatchingKeywordFactory,
    NewsArticleFactory,
)
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from news_articles.models import MatchedSentence, MatchingKeyword, NewsArticle
from news_articles.services.process_matching_article import ProcessMatchingArticle
from officers.factories import OfficerFactory


class ProcessMatchingKeywordsTestCase(TestCase):
    def setUp(self):
        self.pmk = ProcessMatchingArticle()

    def test_process_up_to_date_latest_keywords(self):
        self.pmk.latest_keywords = {"a", "b"}
        self.pmk.last_run_keywords = {"a", "c"}
        self.pmk.match_unprocessed_articles = Mock()
        self.pmk.match_processed_articles = Mock()
        self.pmk.update_status = Mock()

        self.pmk.process()

        self.pmk.match_processed_articles.assert_called()
        self.pmk.match_unprocessed_articles.assert_called()
        self.pmk.update_status.assert_called()

    def test_process_out_of_date_latest_keywords(self):
        self.pmk.latest_keywords = {"a", "b"}
        self.pmk.last_run_keywords = {"a", "b"}
        self.pmk.match_unprocessed_articles = Mock()
        self.pmk.match_processed_articles = Mock()
        self.pmk.update_status = Mock()

        self.pmk.process()

        self.pmk.match_processed_articles.assert_not_called()
        self.pmk.match_unprocessed_articles.assert_called()
        self.pmk.update_status.assert_called()

    def test_match_processed_articles(self):
        self.pmk.latest_keywords = {"a", "b"}
        self.pmk.last_run_keywords = {"a", "c"}
        self.pmk.check_new_keywords = Mock()
        self.pmk.check_deleted_keywords = Mock()

        self.pmk.match_processed_articles()

        self.pmk.check_new_keywords.assert_called_with({"b"})
        self.pmk.check_deleted_keywords.assert_called_with({"c"})

    def test_check_deleted_keywords(self):
        article = NewsArticleFactory()
        matched_sentence = MatchedSentenceFactory(
            article=article, extracted_keywords=["a"]
        )
        officer = OfficerFactory()
        matched_sentence.officers.add(officer)
        matched_sentence.save()

        self.pmk.check_deleted_keywords({"a"})

        count_deleted_items = NewsArticle.objects.filter(
            matched_sentences__officers__isnull=True
        ).count()
        assert count_deleted_items == 1
        assert not MatchedSentence.objects.filter(id=matched_sentence.id)

    def test_check_deleted_keywords_without_keyword(self):
        article = NewsArticleFactory()
        matched_sentence = MatchedSentenceFactory(
            article=article, extracted_keywords=["a"]
        )
        officer = OfficerFactory()
        matched_sentence.officers.add(officer)
        matched_sentence.save()

        self.pmk.check_deleted_keywords({})

        count_deleted_items = NewsArticle.objects.filter(
            matched_sentences__officers__isnull=True
        ).count()
        assert count_deleted_items == 0
        assert MatchedSentence.objects.filter(id=matched_sentence.id)

    def test_check_deleted_keywords_without_delete(self):
        article = NewsArticleFactory()
        matched_sentence = MatchedSentenceFactory(
            article=article, extracted_keywords=["a", "b"]
        )
        officer = OfficerFactory()
        matched_sentence.officers.add(officer)
        matched_sentence.save()

        self.pmk.check_deleted_keywords({"b"})

        count_deleted_items = NewsArticle.objects.filter(
            matched_sentences__officers__isnull=True
        ).count()
        assert count_deleted_items == 0
        sent_result = MatchedSentence.objects.filter(id=matched_sentence.id).first()
        assert sent_result.extracted_keywords == ["a"]

    def test_get_officer_data(self):
        officer1a = OfficerFactory(first_name="first_name1", last_name="last_name1")
        officer1b = OfficerFactory(first_name="first_name1", last_name="last_name1")
        officer2 = OfficerFactory(first_name="first_name2", last_name="last_name2")

        officers_data = self.pmk.get_officer_data()
        expected_result = {
            "first_name1 last_name1": [officer1a.id, officer1b.id],
            "first_name2 last_name2": [officer2.id],
        }

        assert officers_data == expected_result

    def test_update_status(self):
        latest_keywords_obj = MatchingKeywordFactory(keywords=["a"])
        self.pmk.latest_keywords_obj = latest_keywords_obj

        self.pmk.update_status()

        test_latest_keywords_obj = MatchingKeyword.objects.get(
            id=latest_keywords_obj.id
        )
        assert test_latest_keywords_obj.ran_at

    def test_not_update_status(self):
        latest_keywords_obj = MatchingKeywordFactory(keywords=["a"])
        self.pmk.latest_keywords_obj = None

        self.pmk.update_status()

        test_latest_keywords_obj = MatchingKeyword.objects.get(
            id=latest_keywords_obj.id
        )
        assert not test_latest_keywords_obj.ran_at

    def test_match_unprocessed_articles(self):
        NewsArticleFactory(is_processed=True)
        article = NewsArticleFactory(is_processed=False)
        latest_keywords = {"a", "b"}
        self.pmk.latest_keywords = latest_keywords
        self.pmk.create_news_article_matching_data = Mock()

        self.pmk.match_unprocessed_articles()

        articles = NewsArticle.objects.filter(pk=article.pk)

        assert (
            self.pmk.create_news_article_matching_data.call_args[0][0].first().title
            == articles.first().title
        )
        assert (
            self.pmk.create_news_article_matching_data.call_args[0][1]
            == latest_keywords
        )

    def test_check_new_keywords(self):
        article = NewsArticleFactory(is_processed=True)

        self.pmk.update_news_article_matching_data = Mock()

        self.pmk.check_new_keywords({"a"})

        assert (
            self.pmk.update_news_article_matching_data.call_args[0][0].first().title
            == article.title
        )
        assert self.pmk.update_news_article_matching_data.call_args[0][1] == {"a"}

    def test_check_new_keywords_without_keyword(self):
        NewsArticleFactory(is_processed=True)

        self.pmk.update_news_article_matching_data = Mock()

        self.pmk.check_new_keywords({})

        self.pmk.update_news_article_matching_data.assert_not_called()

    @patch("news_articles.services.process_matching_article.NLP.process")
    def test_update_news_article_matching_data(self, mock_nlp_process):
        officer = OfficerFactory()
        exclude_officer = OfficerFactory()
        exclude_obj = ExcludeOfficerFactory(ran_at=None)
        exclude_obj.officers.add(exclude_officer)
        exclude_obj.save()
        mock_nlp_process.return_value = [officer.id, exclude_officer.id]
        self.pmk.officers = self.pmk.get_officer_data()
        sent = "This is abc content."
        article_1 = NewsArticleFactory(
            content=f"{sent} Another sentence here.",
        )
        article_2 = NewsArticleFactory(
            content="This is another abc content. Another sentence here.",
        )
        matched_sentence_2 = MatchedSentenceFactory(
            article=article_2,
            text="This is another abc content.",
            extracted_keywords=["abc"],
        )
        self.pmk.excluded_officers_ids = [exclude_officer.id]
        self.pmk.update_news_article_matching_data(
            [article_1, article_2], {"abc", "another"}
        )

        mock_nlp_process.assert_called_with(sent, self.pmk.officers)

        test_matched_sentence_1 = MatchedSentence.objects.get(text=sent)
        test_matched_sentence_2 = MatchedSentence.objects.get(id=matched_sentence_2.id)

        assert test_matched_sentence_1.extracted_keywords == ["abc"]
        assert test_matched_sentence_1.officers.first() == officer

        assert test_matched_sentence_1.excluded_officers.first() == exclude_officer
        assert not test_matched_sentence_2.officers.count()
        assert sorted(test_matched_sentence_2.extracted_keywords) == sorted(
            ["abc", "another"]
        )

    @patch("news_articles.services.process_matching_article.NLP.process")
    def test_create_news_articles_matching_data(self, mock_nlp_process):
        officer = OfficerFactory()
        exclude_officer = OfficerFactory()
        exclude_obj = ExcludeOfficerFactory(ran_at=None)
        exclude_obj.officers.add(exclude_officer)
        exclude_obj.save()
        mock_nlp_process.return_value = [officer.id, exclude_officer.id]
        self.pmk.officers = self.pmk.get_officer_data()
        sent_1 = "This is abc content."
        article_1 = NewsArticleFactory(
            content=f"{sent_1} Another sentence here.",
            is_processed=False,
        )
        sent_2 = "This is another abc content."
        article_2 = NewsArticleFactory(
            content=f"{sent_2} Unused sentence here.",
            is_processed=False,
        )
        self.pmk.excluded_officers_ids = [exclude_officer.id]
        self.pmk.create_news_article_matching_data(
            [article_1, article_2], {"abc", "another"}
        )

        article_1.refresh_from_db()
        article_2.refresh_from_db()

        assert article_1.is_processed
        assert article_2.is_processed
        assert article_1.matched_sentences.all().count() == 1
        assert article_1.matched_sentences.first().text == sent_1
        assert sorted(article_1.matched_sentences.first().extracted_keywords) == sorted(
            ["abc"]
        )
        assert article_1.matched_sentences.first().officers.first() == officer
        assert (
            article_1.matched_sentences.first().excluded_officers.first()
            == exclude_officer
        )
        assert article_2.matched_sentences.all().count() == 1
        assert article_2.matched_sentences.first().text == sent_2
        assert sorted(article_2.matched_sentences.first().extracted_keywords) == sorted(
            ["abc", "another"]
        )
        assert article_2.matched_sentences.first().officers.first() == officer
        assert (
            article_2.matched_sentences.first().excluded_officers.first()
            == exclude_officer
        )
