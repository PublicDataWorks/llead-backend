from functools import wraps

from django.core.cache import cache
from django.urls import reverse

from rest_framework.response import Response

from departments.models import Department
from news_articles.models import MatchedSentence
from officers.models import Officer


def custom_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request = args[1]
        request_path = request.get_full_path()
        response_data = cache.get(request_path)

        if not response_data:
            response = func(*args, **kwargs)
            response_data = response.data
            cache.set(request_path, response_data)

        return Response(response_data)

    return wrapper


def flush_news_article_related_caches(start_time=None):
    if start_time:
        matched_sentences = MatchedSentence.objects.filter(updated_at__gt=start_time)
    else:
        matched_sentences = MatchedSentence.objects.all()
    officers = Officer.objects.filter(matched_sentences__in=matched_sentences)
    departments = Department.objects.filter(officers__in=officers).distinct()

    delete_cache("api:analytics-summary")

    for officer in officers:
        delete_cache("api:officers-timeline", url_kwargs={"pk": officer.id})

    for department in departments:
        delete_cache(
            "api:departments-detail", url_kwargs={"pk": department.agency_slug}
        )
        delete_cache(
            "api:departments-news-articles", url_kwargs={"pk": department.agency_slug}
        )


def delete_cache(pattern, url_kwargs=None):
    cache.delete(reverse(pattern, kwargs=url_kwargs))
