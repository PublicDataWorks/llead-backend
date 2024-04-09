from collections import defaultdict

from django.db.models import Q

from tqdm import tqdm

from news_articles.models import ExcludeOfficer, MatchedSentence
from officers.models import Officer
from utils.nlp import NLP


class ProcessRematchOfficers:
    def __init__(self, start_time):
        self.start_time = start_time

        updated_officers = self.get_updated_officers()
        created_officers = Officer.objects.filter(created_at__gte=self.start_time)
        self.officers = self.get_officers_data([*updated_officers, *created_officers])

        self.nlp = NLP()

        latest_exclude_officers = ExcludeOfficer.objects.order_by("-created_at").first()
        self.excluded_officers_ids = (
            latest_exclude_officers.officers.values_list("id", flat=True)
            if latest_exclude_officers
            else []
        )

    def get_updated_officers(self):
        updated_officers = Officer.objects.filter(is_name_changed=True)
        for officer in updated_officers:
            officer.matched_sentences.clear()
            officer.is_name_changed = False

        Officer.objects.bulk_update(updated_officers, ["is_name_changed"])
        return updated_officers

    def get_officers_data(self, officers):
        officers_data = defaultdict(list)

        for officer in officers:
            officers_data[officer.name].append(officer.id)

        return officers_data

    def process(self):
        if len(self.officers):
            matched_sentences = MatchedSentence.objects.all()

            for matched_sentence in tqdm(
                matched_sentences, desc="Match officers with existed sentences"
            ):
                matched_officers = self.nlp.process(
                    matched_sentence.text, self.officers
                )
                matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & ~Q(id__in=self.excluded_officers_ids)
                )
                exclude_matched_officers_obj = Officer.objects.filter(
                    Q(id__in=matched_officers) & Q(id__in=self.excluded_officers_ids)
                )

                matched_sentence.officers.add(*matched_officers_obj)
                matched_sentence.excluded_officers.add(*exclude_matched_officers_obj)
                matched_sentence.save()

        return False
