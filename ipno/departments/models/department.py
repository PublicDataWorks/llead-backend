from django.contrib.postgres.fields import ArrayField
from django.db import models

from mapbox_location_field.models import LocationField

from utils.models import TimeStampsModel


class Department(TimeStampsModel):
    slug = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    parish = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    location_map_url = models.CharField(max_length=255, null=True, blank=True)
    location = LocationField(null=True, blank=True, map_attrs={"readonly": False})
    data_period = ArrayField(models.IntegerField(), default=list, null=True, blank=True)
    aliases = ArrayField(
        models.CharField(max_length=255), default=list, null=True, blank=True
    )
    officer_fraction = models.FloatField(null=True, blank=True)

    starred_officers = models.ManyToManyField(
        "officers.Officer",
        blank=True,
        related_name="starred_departments",
    )

    starred_news_articles = models.ManyToManyField(
        "news_articles.NewsArticle",
        blank=True,
        related_name="starred_departments",
    )

    starred_documents = models.ManyToManyField(
        "documents.Document",
        blank=True,
        related_name="starred_departments",
    )

    def __str__(self):
        return f"{self.name} - {self.id}"
