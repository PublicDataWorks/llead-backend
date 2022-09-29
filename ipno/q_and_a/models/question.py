from django.db import models

from utils.models import TimeStampsModel
from martor.models import MartorField


class Question(TimeStampsModel):
    question = models.TextField()
    answer = MartorField(blank=True, null=True)

    section = models.ForeignKey('q_and_a.section', on_delete=models.CASCADE, related_name='questions')
