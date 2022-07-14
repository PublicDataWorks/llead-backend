from django.db import models

from utils.models import TimeStampsModel


class Question(TimeStampsModel):
    question = models.TextField()
    answer = models.TextField()

    section = models.ForeignKey('q_and_a.section', on_delete=models.CASCADE, related_name='questions')
