from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from documents.models import Document
from news_articles.models import NewsArticle
from officers.models import Officer
from departments.models import Department
from historical_data.constants import (
    RECENT_DEPARTMENT_TYPE,
    RECENT_DOCUMENT_TYPE,
    RECENT_NEWS_ARTICLE_TYPE,
    RECENT_OFFICER_TYPE,
)
from shared.serializers import (
    DepartmentSerializer,
    OfficerSerializer,
    NewsArticleSerializer
)
from shared.serializers import DocumentSerializer


class HistoricalDataViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='recent-items')
    def recent_items(self, request):
        user = request.user
        user_recent_items = user.recent_items

        recent_search_data = []

        if user_recent_items:
            department_ids = []
            officer_ids = []
            document_ids = []
            news_article_ids = []

            ids_type_mapping = {
                RECENT_DEPARTMENT_TYPE: department_ids,
                RECENT_OFFICER_TYPE: officer_ids,
                RECENT_DOCUMENT_TYPE: document_ids,
                RECENT_NEWS_ARTICLE_TYPE: news_article_ids
            }

            for recent_item in user_recent_items:
                ids_type_mapping[recent_item['type']].append(recent_item['id'])

            departments = Department.objects.filter(slug__in=department_ids)
            officers = Officer.objects.prefetch_events().filter(id__in=officer_ids)
            documents = Document.objects.prefetch_departments().filter(id__in=document_ids)
            news_articles = NewsArticle.objects.prefetch_related('source').filter(id__in=news_article_ids)

            recent_objects_mapping = {
                RECENT_DEPARTMENT_TYPE: {
                    'query': {
                        department.slug: department for department in departments
                    },
                    'serializer': DepartmentSerializer,
                },
                RECENT_OFFICER_TYPE: {
                    'query': {
                        officer.id: officer for officer in officers
                    },
                    'serializer': OfficerSerializer,
                },
                RECENT_DOCUMENT_TYPE: {
                    'query': {
                        document.id: document for document in documents
                    },
                    'serializer': DocumentSerializer,
                },
                RECENT_NEWS_ARTICLE_TYPE: {
                    'query': {
                        news_article.id: news_article for news_article in news_articles
                    },
                    'serializer': NewsArticleSerializer,
                },
            }

            for user_recent_item in user_recent_items:
                item_type = user_recent_item['type']
                recent_object = recent_objects_mapping.get(item_type)

                item_id = user_recent_item.get('id') if user.recent_items else None
                item = recent_object['query'].get(item_id) if item_id else None

                if item:
                    recent_data = recent_object['serializer'](item).data
                    recent_data['type'] = item_type

                    recent_search_data.append(recent_data)

        return Response(recent_search_data)

    @recent_items.mapping.post
    def update_recent_items(self, request):
        recent_item = request.data
        new_item = {
            "id": recent_item.get('id'),
            "type": recent_item.get('type')
        }

        user = request.user
        user_recent_items = user.recent_items or []

        if new_item in user_recent_items:
            user_recent_items.remove(new_item)
        user_recent_items.insert(0, new_item)

        user.recent_items = user_recent_items[:10]
        user.save()

        return Response({"detail": "updated user recent items"})

    @recent_items.mapping.delete
    def delete_recent_item(self, request):
        recent_item = request.query_params

        item_id = recent_item.get('id')
        item_type = recent_item.get('type')

        if not item_id or not item_type:
            return Response({"error": "id and type is required"}, status=status.HTTP_400_BAD_REQUEST)

        new_item = {
            "id": int(item_id) if item_id.isdigit() else item_id,
            "type": item_type
        }

        user = request.user
        user_recent_items = user.recent_items or []

        if new_item not in user_recent_items:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user_recent_items.remove(new_item)
        user.save()
        return Response({"detail": "deleted user recent item"})

    @action(detail=False, methods=['get'], url_path='recent-queries')
    def recent_queries(self, request):
        user = request.user
        user_recent_queries = user.recent_queries

        return Response(user_recent_queries)

    @recent_queries.mapping.post
    def update_recent_queries(self, request):
        recent_query = request.data['q']

        user = request.user
        user_recent_queries = user.recent_queries or []

        if recent_query in user_recent_queries:
            user_recent_queries.remove(recent_query)
        user_recent_queries.insert(0, recent_query)

        user.recent_queries = user_recent_queries[:10]
        user.save()

        return Response({"detail": "updated user recent queries"})
