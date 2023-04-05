from django.core.management.base import BaseCommand

from authentication.models import User
from historical_data.models import AnonymousItem, AnonymousQuery
from news_articles.models import NewsArticle


class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.all().delete()
        admin = User(email="admin@gmail.com", is_admin=True)
        admin.set_password("P@ssw0rd")
        admin.save()

        test_user = User(email="test@gmail.com")
        test_user.set_password("P@ssw0rd")
        test_user.save()

        NewsArticle.objects.filter(
            pk__in=NewsArticle.objects.order_by("-id").values("pk")[:10000]
        ).delete()

        AnonymousItem.objects.all().delete()
        AnonymousQuery.objects.all().delete()
