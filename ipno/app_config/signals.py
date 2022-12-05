from django.db.models.signals import post_save
from django.dispatch import receiver

from app_config.models import (
    AppTextContent,
    AppValueConfig,
    FrontPageCard,
    FrontPageOrder,
)
from utils.cache_utils import delete_cache


@receiver(post_save, sender=AppValueConfig)
@receiver(post_save, sender=AppTextContent)
def app_config_cache(*args, **kwargs):
    delete_cache("api:app-config-list")


@receiver(post_save, sender=FrontPageCard)
def front_page_card_cache(*args, **kwargs):
    delete_cache("api:front-page-cards-list")


@receiver(post_save, sender=FrontPageOrder)
def front_page_order_cache(*args, **kwargs):
    delete_cache("api:front-page-orders-list")
