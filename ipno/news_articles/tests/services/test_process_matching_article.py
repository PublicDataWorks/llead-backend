from unittest.mock import Mock, patch

from django.conf import settings
from django.db.models import F
from django.test import TestCase

from data.constants import NEWS_ARTICLE_OFFICER_MODEL_NAME
from data.factories import WrglRepoFactory
from data.models import WrglRepo
from news_articles.constants import NEWS_ARTICLE_OFFICER_WRGL_COLUMNS
from news_articles.factories import NewsArticleFactory, MatchingKeywordFactory
from news_articles.models import NewsArticle, MatchingKeyword
from news_articles.services.process_matching_article import ProcessMatchingArticle
from officers.factories import OfficerFactory


class ProcessMatchingKeywordsTestCase(TestCase):
    def setUp(self):
        self.pmk = ProcessMatchingArticle()

    def test_process_up_to_date_latest_keywords(self):
        self.pmk.latest_keywords = {'a', 'b'}
        self.pmk.last_run_keywords = {'a', 'c'}
        self.pmk.match_unprocessed_articles = Mock()
        self.pmk.match_processed_articles = Mock()
        self.pmk.update_status = Mock()
        self.pmk.commit_data_to_wrgl = Mock()

        self.pmk.process()

        self.pmk.match_processed_articles.assert_called()
        self.pmk.match_unprocessed_articles.assert_called()
        self.pmk.update_status.assert_called()
        self.pmk.commit_data_to_wrgl.assert_called()

    def test_process_out_of_date_latest_keywords(self):
        self.pmk.latest_keywords = {'a', 'b'}
        self.pmk.last_run_keywords = {'a', 'b'}
        self.pmk.match_unprocessed_articles = Mock()
        self.pmk.match_processed_articles = Mock()
        self.pmk.update_status = Mock()
        self.pmk.commit_data_to_wrgl = Mock()

        self.pmk.process()

        self.pmk.match_processed_articles.assert_not_called()
        self.pmk.match_unprocessed_articles.assert_called()
        self.pmk.update_status.assert_called()
        self.pmk.commit_data_to_wrgl.assert_called()

    def test_match_processed_articles(self):
        self.pmk.latest_keywords = {'a', 'b'}
        self.pmk.last_run_keywords = {'a', 'c'}
        self.pmk.check_new_keywords = Mock()
        self.pmk.check_deleted_keywords = Mock()

        self.pmk.match_processed_articles()

        self.pmk.check_new_keywords.assert_called_with({'b'})
        self.pmk.check_deleted_keywords.assert_called_with({'c'})

    def test_check_deleted_keywords(self):
        article = NewsArticleFactory(extracted_keywords=['a'])
        officer = OfficerFactory()
        article.officers.add(officer)
        article.save()

        self.pmk.check_deleted_keywords({'a'})

        count_deleted_items = NewsArticle.objects.filter(officers__isnull=True).count()
        assert count_deleted_items == 1

    def test_check_deleted_keywords_without_delete(self):
        article = NewsArticleFactory(extracted_keywords=['a'])
        officer = OfficerFactory()
        article.officers.add(officer)
        article.save()

        self.pmk.check_deleted_keywords({'b'})

        count_deleted_items = NewsArticle.objects.filter(officers__isnull=True).count()
        assert count_deleted_items == 0

    def test_get_officer_data(self):
        officer1a = OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer1b = OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer2 = OfficerFactory(first_name='first_name2', last_name='last_name2')

        officers_data = self.pmk.get_officer_data()
        expected_result = {
            'first_name1 last_name1': [officer1a.id, officer1b.id],
            'first_name2 last_name2': [officer2.id]
        }

        assert officers_data == expected_result

    def test_update_status(self):
        latest_keywords_obj = MatchingKeywordFactory(keywords=['a'])
        self.pmk.latest_keywords_obj = latest_keywords_obj

        self.pmk.update_status()

        test_latest_keywords_obj = MatchingKeyword.objects.get(id=latest_keywords_obj.id)
        assert test_latest_keywords_obj.ran_at

    def test_not_update_status(self):
        latest_keywords_obj = MatchingKeywordFactory(keywords=['a'])
        self.pmk.latest_keywords_obj = None

        self.pmk.update_status()

        test_latest_keywords_obj = MatchingKeyword.objects.get(id=latest_keywords_obj.id)
        assert not test_latest_keywords_obj.ran_at

    def test_match_unprocessed_articles(self):
        NewsArticleFactory(extracted_keywords=['a', 'b'])
        article = NewsArticleFactory()
        latest_keywords = {'a', 'b'}
        self.pmk.latest_keywords = latest_keywords
        self.pmk.update_news_article_matching_data = Mock()

        self.pmk.match_unprocessed_articles()

        articles = NewsArticle.objects.filter(pk=article.pk)

        assert self.pmk.update_news_article_matching_data.call_args[0][0].first().title == articles.first().title
        assert self.pmk.update_news_article_matching_data.call_args[0][1] == latest_keywords

    def test_check_new_keywords(self):
        NewsArticleFactory(extracted_keywords=['a', 'b'])

        self.pmk.update_news_article_matching_data = Mock()

        self.pmk.check_new_keywords({'a'})

        articles = NewsArticle.objects.filter(extracted_keywords__isnull=False)

        assert self.pmk.update_news_article_matching_data.call_args[0][0].first().title == articles.first().title
        assert self.pmk.update_news_article_matching_data.call_args[0][1] == {'a'}

    def test_commit_data_to_wrgl(self):
        news = NewsArticleFactory()
        officer = OfficerFactory()
        news.officers.add(officer)
        WrglRepoFactory(
            data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_OFFICER_WRGL_REPO,
            commit_hash='old_commit',
        )

        def mock_generate_csv_file_side_effect(data, columns):
            return data

        mock_generate_csv_file = Mock()
        mock_generate_csv_file.side_effect = mock_generate_csv_file_side_effect
        mock_create_wrgl_commit = Mock()

        mock_json = Mock()
        mock_json.return_value = {
            "hash": "hash",
            "contentHash": "contentHash"
        }
        mock_response_object = Mock(json=mock_json)
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.pmk.wrgl = mock_wrgl_generator_object

        news_officers = NewsArticle.officers.through.objects.annotate(
                    uid=F('officer__uid'),
                    created_at=F('newsarticle__created_at')
                ).all()
        self.pmk.latest_keywords = {'a'}

        self.pmk.commit_data_to_wrgl()

        assert mock_generate_csv_file.call_args[0][0].first().uid == news_officers.first().uid
        assert mock_generate_csv_file.call_args[0][1] == NEWS_ARTICLE_OFFICER_WRGL_COLUMNS

        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][0] == 'news_article_officer'
        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][1] == '+ 1 keyword(s)'
        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][2] == 'id'
        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][3].first().uid == news_officers.first().uid

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    def test_not_updating_commit_hash(self):
        news = NewsArticleFactory()
        officer = OfficerFactory()
        news.officers.add(officer)

        WrglRepoFactory(
            data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_OFFICER_WRGL_REPO,
            commit_hash='hash',
        )

        def mock_generate_csv_file_side_effect(data, columns):
            return data

        mock_generate_csv_file = Mock()
        mock_generate_csv_file.side_effect = mock_generate_csv_file_side_effect
        mock_create_wrgl_commit = Mock()

        mock_json = Mock()
        mock_json.return_value = {
            "hash": "hash",
            "contentHash": "contentHash"
        }
        mock_response_object = Mock(json=mock_json)
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.pmk.wrgl = mock_wrgl_generator_object

        news_officers = NewsArticle.officers.through.objects.annotate(
            uid=F('officer__uid'),
            created_at=F('newsarticle__created_at')
        ).all()
        self.pmk.latest_keywords = {'a'}

        self.pmk.commit_data_to_wrgl()

        assert mock_generate_csv_file.call_args[0][0].first().uid == news_officers.first().uid
        assert mock_generate_csv_file.call_args[0][1] == NEWS_ARTICLE_OFFICER_WRGL_COLUMNS

        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][0] == 'news_article_officer'
        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][1] == '+ 1 keyword(s)'
        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][2] == 'id'
        assert self.pmk.wrgl.create_wrgl_commit.call_args[0][3].first().uid == news_officers.first().uid

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    def test_not_commit_data_to_wrgl(self):
        WrglRepoFactory(
            data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_OFFICER_WRGL_REPO,
            commit_hash='hash',
        )

        self.pmk.commit_data_to_wrgl()

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    @patch('news_articles.services.process_matching_article.NLP.process')
    def test_update_news_article_matching_data(self, mock_nlp_process):
        officer = OfficerFactory()
        mock_nlp_process.return_value = [officer.id]
        self.pmk.officers = self.pmk.get_officer_data()

        article_1 = NewsArticleFactory(
            content='this is a content',
            extracted_keywords=[]
        )
        article_2 = NewsArticleFactory(
            content='this is a content',
            extracted_keywords=['a']
        )

        self.pmk.update_news_article_matching_data([article_1, article_2], {'a'})

        mock_nlp_process.assert_called_with(article_1.content, self.pmk.officers)

        test_article_1 = NewsArticle.objects.get(id=article_1.id)
        test_article_2 = NewsArticle.objects.get(id=article_2.id)

        assert test_article_1.extracted_keywords == ['a']
        assert test_article_1.officers.first() == officer
        assert not test_article_2.officers.count()
