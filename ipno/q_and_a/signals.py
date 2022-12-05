from django.db.models.signals import post_save
from django.dispatch import receiver

from q_and_a.models import Question, Section
from utils.cache_utils import delete_cache


@receiver(post_save, sender=Section)
@receiver(post_save, sender=Question)
def app_config_cache(*args, **kwargs):
    delete_cache("api:q-and-a-list")
