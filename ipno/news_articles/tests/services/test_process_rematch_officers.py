from unittest.mock import Mock, call

from django.test import TestCase
from django.utils import timezone
from django.db.models import F
from django.conf import settings

from data.constants import NEWS_ARTICLE_OFFICER_MODEL_NAME
from data.factories import WrglRepoFactory
from data.models import WrglRepo
from news_articles.constants import NEWS_ARTICLE_OFFICER_WRGL_COLUMNS
from news_articles.factories import NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from news_articles.models import MatchedSentence
from news_articles.services import ProcessRematchOfficers
from officers.factories import OfficerFactory


class ProcessRematchOfficersTestCase(TestCase):
    def setUp(self):
        start_time = timezone.now()
        self.pro = ProcessRematchOfficers(start_time)

    def test_get_updated_officers(self):
        officer = OfficerFactory(is_name_changed=True)
        sent = MatchedSentenceFactory()
        sent.officers.add(officer)
        sent.save()

        result = self.pro.get_updated_officers()

        updated_sent = MatchedSentence.objects.get(id=sent.id)
        assert not (officer in updated_sent.officers.all())
        assert result[0].id == officer.id

    def test_get_officer_data(self):
        officer1a = OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer1b = OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer2 = OfficerFactory(first_name='first_name2', last_name='last_name2')

        officers_data = self.pro.get_officers_data([
            officer1a,
            officer1b,
            officer2,
        ])

        expected_result = {
            'first_name1 last_name1': [officer1a.id, officer1b.id],
            'first_name2 last_name2': [officer2.id]
        }

        assert officers_data == expected_result

    def test_commit_data_to_wrgl(self):
        news = NewsArticleFactory()
        officer = OfficerFactory()
        matched_sentence = MatchedSentenceFactory(article=news)
        matched_sentence.officers.add(officer)
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

        mock_response_object = Mock(sum="hash")
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.pro.wrgl = mock_wrgl_generator_object

        MatchedSentenceOfficer = MatchedSentence.officers.through
        data = MatchedSentenceOfficer.objects.order_by(
            'officer_id',
            'matchedsentence__article__id'
        ).annotate(
            uid=F('officer__uid'),
            created_at=F('matchedsentence__created_at'),
            newsarticle_id=F('matchedsentence__article__id'),
        ).all()
        self.pro.officers = [officer]

        self.pro.commit_data_to_wrgl()

        assert mock_generate_csv_file.call_args[0][0].first().uid == data.first().uid
        assert mock_generate_csv_file.call_args[0][1] == NEWS_ARTICLE_OFFICER_WRGL_COLUMNS

        assert self.pro.wrgl.create_wrgl_commit.call_args[0][0] == 'data'
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][1] == '+ 1 officer(s)'
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][2] == ['uid', 'newsarticle_id']
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][3].first().uid == data.first().uid
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][4] == 'news_article_officer'

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    def test_process_without_officers(self):
        self.pro.officers = []

        result = self.pro.process()

        assert not result

    def test_process_with_officers(self):
        OfficerFactory(first_name='first_name1', last_name='last_name1')
        OfficerFactory(first_name='first_name1', last_name='last_name1')
        officer2 = OfficerFactory(first_name='first_name2', last_name='last_name2')
        officer3 = OfficerFactory(first_name='first_name3', last_name='last_name3')

        sent1 = MatchedSentenceFactory()
        sent2 = MatchedSentenceFactory()

        def process_side_effect(text, officers):
            if text == sent1.text:
                return [officer2.id, officer3.id]
            else:
                return []

        self.pro.nlp.process = Mock()
        self.pro.nlp.process.side_effect = process_side_effect

        self.pro.excluded_officers_ids = [officer3.id]
        self.pro.officers = self.pro.get_officers_data([officer2, officer3])

        self.pro.commit_data_to_wrgl = Mock(return_value=True)

        self.pro.process()

        expected_calls = [
            call(sent1.text, self.pro.officers),
            call(sent2.text, self.pro.officers),
        ]
        self.pro.nlp.process.assert_has_calls(expected_calls)
        self.pro.commit_data_to_wrgl.assert_called()

        assert officer2 in sent1.officers.all()
        assert officer3 in sent1.excluded_officers.all()

    def test_not_commit_data_to_wrgl(self):
        WrglRepoFactory(
            data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_OFFICER_WRGL_REPO,
            commit_hash='hash',
        )

        self.pro.commit_data_to_wrgl()

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    def test_not_updating_commit_hash(self):
        news = NewsArticleFactory()
        officer = OfficerFactory()
        matched_sentence = MatchedSentenceFactory(article=news)
        matched_sentence.officers.add(officer)
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

        mock_response_object = Mock(sum="hash")
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.pro.wrgl = mock_wrgl_generator_object

        MatchedSentenceOfficer = MatchedSentence.officers.through
        data = MatchedSentenceOfficer.objects.order_by(
            'officer_id',
            'matchedsentence__article__id'
        ).annotate(
            uid=F('officer__uid'),
            created_at=F('matchedsentence__created_at'),
            newsarticle_id=F('matchedsentence__article__id'),
        ).all()
        self.pro.officers = [officer]

        self.pro.commit_data_to_wrgl()

        assert mock_generate_csv_file.call_args[0][0].first().uid == data.first().uid
        assert mock_generate_csv_file.call_args[0][1] == NEWS_ARTICLE_OFFICER_WRGL_COLUMNS

        assert self.pro.wrgl.create_wrgl_commit.call_args[0][0] == 'data'
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][1] == '+ 1 officer(s)'
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][2] == ['uid', 'newsarticle_id']
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][3].first().uid == data.first().uid
        assert self.pro.wrgl.create_wrgl_commit.call_args[0][4] == 'news_article_officer'

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'
