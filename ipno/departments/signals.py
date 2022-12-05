from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from departments.models import Department


@receiver(post_save, sender=Department)
def department_cache(*args, **kwargs):
    cache.clear()
