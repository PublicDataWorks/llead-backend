"""ipno URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import re_path, include, path
from django.views.generic.base import RedirectView

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django_rest_passwordreset.views import reset_password_request_token

from departments.views import DepartmentsViewSet
from documents.views import DocumentsViewSet
from app_config.views import AppConfigViewSet, FrontPageOrdersViewSet, FrontPageCardsViewSet
from analytics.views import AnalyticsViewSet
from feedbacks.views import FeedbackViewSet
from news_articles.views import NewsArticlesViewSet
from officers.views import OfficersViewSet
from q_and_a.views import QAndAViewSet
from search.views import SearchViewSet
from authentication.views import TokenRevokeView, UserView, CustomPasswordTokenVerificationView
from status.views import StatusView
from historical_data.views import HistoricalDataViewSet

api_router = routers.SimpleRouter()

api_router.register(r'documents', DocumentsViewSet, basename='documents')
api_router.register(r'departments', DepartmentsViewSet, basename='departments')
api_router.register(r'app-config', AppConfigViewSet, basename='app-config')
api_router.register(r'q-and-a', QAndAViewSet, basename='q-and-a')
api_router.register(r'feedbacks', FeedbackViewSet, basename='feedbacks')
api_router.register(r'analytics', AnalyticsViewSet, basename='analytics')
api_router.register(r'officers', OfficersViewSet, basename='officers')
api_router.register(r'search', SearchViewSet, basename='search')
api_router.register(r'historical-data', HistoricalDataViewSet, basename='historical-data')
api_router.register(r'news-articles', NewsArticlesViewSet, basename='news-articles')
api_router.register(r'front-page-orders', FrontPageOrdersViewSet, basename='front-page-orders')
api_router.register(r'front-page-cards', FrontPageCardsViewSet, basename='front-page-cards')


urlpatterns = [
    path('', RedirectView.as_view(url='admin/')),
    path('admin/', admin.site.urls),
    re_path(r'^api/', include((api_router.urls, 'api'), namespace='api')),
    path('api/token/', TokenObtainPairView.as_view(), name='token'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('api/token/revoke/', TokenRevokeView.as_view(), name='revoke_token'),
    path('api/user/', UserView.as_view(), name='user'),
    path('api/status/', StatusView.as_view(), name='status'),
    path('martor/', include('martor.urls')),
    path('api/password-reset/', reset_password_request_token, name="reset-password-request"),
    path('api/password-reset/confirm/', CustomPasswordTokenVerificationView.as_view(), name="reset-password-confirm"),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
