from django.utils import timezone

from news_articles.models import ExcludeOfficer, MatchedSentence


class ProcessExcludeArticleOfficer:
    def __init__(self):
        self.latest_exclude_officers_obj = ExcludeOfficer.objects.order_by('-created_at').first()
        self.last_run_exclude_obj = ExcludeOfficer.objects.filter(ran_at__isnull=False).order_by('-created_at').first()

        self.latest_exclude_officers = set(self.latest_exclude_officers_obj.officers.all()) if self.latest_exclude_officers_obj else set()
        self.last_run_exclude = set(self.last_run_exclude_obj.officers.all()) if self.last_run_exclude_obj else set()

    def process(self):
        inserted_officers = self.latest_exclude_officers - self.last_run_exclude
        deleted_officers = self.last_run_exclude - self.latest_exclude_officers
        sentences = MatchedSentence.objects.all()
        updated_sents = False

        for sent in sentences:
            common_inserted_officers = set(inserted_officers) & set(sent.officers.all())
            common_deleted_officers = set(deleted_officers) & set(sent.excluded_officers.all())

            if common_inserted_officers:
                updated_sents = True
                sent.officers.remove(*common_inserted_officers)
                sent.excluded_officers.add(*common_inserted_officers)

            if common_deleted_officers:
                updated_sents = True
                sent.excluded_officers.remove(*common_deleted_officers)
                sent.officers.add(*common_deleted_officers)

            sent.save()

        self.update_status()
        return updated_sents

    def update_status(self):
        if self.latest_exclude_officers_obj:
            self.latest_exclude_officers_obj.ran_at = timezone.now()
            self.latest_exclude_officers_obj.save()
