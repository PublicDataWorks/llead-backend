from collections import defaultdict
from tqdm import tqdm

from django.conf import settings
from django.db.models import F, Q

from data.constants import NEWS_ARTICLE_OFFICER_MODEL_NAME
from data.models import WrglRepo
from news_articles.constants import NEWS_ARTICLE_OFFICER_WRGL_COLUMNS
from news_articles.models import MatchedSentence, ExcludeOfficer
from officers.models import Officer
from utils.nlp import NLP
from utils.wrgl_generator import WrglGenerator


class ProcessRematchOfficers:
    def __init__(self, start_time):
        self.start_time = start_time

        updated_officers = self.get_updated_officers()
        created_officers = Officer.objects.filter(created_at__gte=self.start_time)
        self.officers = self.get_officers_data([*updated_officers, *created_officers])

        self.nlp = NLP()
        self.wrgl = WrglGenerator()

        latest_exclude_officers = ExcludeOfficer.objects.order_by('-created_at').first()
        self.excluded_officers_ids = latest_exclude_officers.officers.values_list(
            'id',
            flat=True
        ) if latest_exclude_officers else []

    def get_updated_officers(self):
        updated_officers = Officer.objects.filter(is_name_changed=True)
        for officer in updated_officers:
            officer.matched_sentences.clear()
            officer.is_name_changed = False

        Officer.objects.bulk_update(updated_officers, ['is_name_changed'])
        return updated_officers

    def get_officers_data(self, officers):
        officers_data = defaultdict(list)

        for officer in officers:
            officers_data[officer.name].append(officer.id)

        return officers_data

    def process(self):
        if len(self.officers):
            matched_sentences = MatchedSentence.objects.all()

            for matched_sentence in tqdm(matched_sentences, desc='Match officers with existed sentences'):
                matched_officers = self.nlp.process(matched_sentence.text, self.officers)
                matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & ~Q(id__in=self.excluded_officers_ids)
                )
                exclude_matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & Q(id__in=self.excluded_officers_ids)
                )

                matched_sentence.officers.add(*matched_officers_obj)
                matched_sentence.excluded_officers.add(*exclude_matched_officers_obj)
                matched_sentence.save()

            return self.commit_data_to_wrgl()

        return False

    def commit_data_to_wrgl(self):
        MatchedSentenceOfficer = MatchedSentence.officers.through
        data = MatchedSentenceOfficer.objects.order_by(
            'officer_id',
            'matchedsentence__article__id'
        ).annotate(
            uid=F('officer__uid'),
            created_at=F('matchedsentence__created_at'),
            newsarticle_id=F('matchedsentence__article__id'),
        ).all()

        count_updated_objects = data.filter(matchedsentence__updated_at__gte=self.start_time).count()

        if count_updated_objects:
            columns = NEWS_ARTICLE_OFFICER_WRGL_COLUMNS
            gzexcel = self.wrgl.generate_csv_file(data, columns)

            response = self.wrgl.create_wrgl_commit(
                settings.NEWS_ARTICLE_OFFICER_WRGL_REPO,
                f'+ {len(self.officers)} officer(s)',
                'uid,newsarticle_id',
                gzexcel
            )

            commit_hash = response.json()['hash']
            wrgl_repo = WrglRepo.objects.get(data_model=NEWS_ARTICLE_OFFICER_MODEL_NAME)

            if commit_hash and wrgl_repo.commit_hash != commit_hash:
                wrgl_repo.commit_hash = commit_hash
                wrgl_repo.save()

        return count_updated_objects > 0
