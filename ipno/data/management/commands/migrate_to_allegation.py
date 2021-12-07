from django.core.management import BaseCommand

from data.models import WrglRepo
from data.services import NewComplaintImporter
from utils.count_complaints import count_complaints


class Command(BaseCommand):
    def handle(self, *args, **options):
        complaint = WrglRepo.objects.filter(repo_name='complaint').first()
        if complaint:
            complaint.repo_name = 'allegation'
            complaint.commit_hash = ''
            complaint.save()

        new_complaint_imported = NewComplaintImporter().process()

        if new_complaint_imported:
            count_complaints()
