import datetime
from functools import cached_property

import pytz
from rest_framework import serializers

from app_config.constants import DEFAULT_RECENT_DAYS
from app_config.models import AppConfig
from complaints.constants import ALLEGATION_DISPOSITION_SUSTAINED
from news_articles.models import MatchedSentence, NewsArticle
from officers.constants import UOF_OCCUR
from utils.data_utils import format_data_period


class DepartmentDetailsSerializer(serializers.Serializer):
    id = serializers.CharField(source='slug')
    name = serializers.CharField()
    city = serializers.CharField()
    parish = serializers.CharField()
    phone = serializers.CharField()
    address = serializers.CharField()
    location_map_url = serializers.CharField()

    officers_count = serializers.SerializerMethodField()
    datasets_count = serializers.SerializerMethodField()
    recent_datasets_count = serializers.SerializerMethodField()
    news_articles_count = serializers.SerializerMethodField()
    recent_news_articles_count = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    sustained_complaints_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    recent_documents_count = serializers.SerializerMethodField()
    incident_force_count = serializers.SerializerMethodField()
    data_period = serializers.SerializerMethodField()

    @cached_property
    def _get_recent_day(self):
        recent_date_config = AppConfig.objects.filter(name='ANALYTIC_RECENT_DAYS').first()
        recent_date = int(recent_date_config.value) if recent_date_config else DEFAULT_RECENT_DAYS

        return datetime.datetime.now(pytz.utc) - datetime.timedelta(days=recent_date)

    def get_officers_count(self, obj):
        return obj.officers.filter(canonical_person__isnull=False).distinct().count()

    def get_news_articles_count(self, obj):
        officers = obj.officers.all()
        matched_sentences = MatchedSentence.objects.filter(officers__in=officers).all()

        return NewsArticle.objects.filter(matched_sentences__in=matched_sentences).distinct().count()

    def get_recent_news_articles_count(self, obj):
        officers = obj.officers.all()
        matched_sentences = MatchedSentence.objects.filter(officers__in=officers).all()

        return NewsArticle.objects.filter(
            matched_sentences__in=matched_sentences,
            published_date__gt=self._get_recent_day,
        ).distinct().count()

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_recent_documents_count(self, obj):
        return obj.documents.filter(created_at__gt=self._get_recent_day).count()

    def get_datasets_count(self, obj):
        return obj.wrgl_files.count()

    def get_recent_datasets_count(self, obj):
        return obj.wrgl_files.filter(created_at__gt=self._get_recent_day).count()

    def get_complaints_count(self, obj):
        return obj.complaints.count()

    def get_sustained_complaints_count(self, obj):
        return obj.complaints.filter(disposition=ALLEGATION_DISPOSITION_SUSTAINED).count()

    def get_incident_force_count(self, obj):
        return obj.events.filter(kind=UOF_OCCUR).count()

    def get_data_period(self, obj):
        return format_data_period(obj.data_period)
