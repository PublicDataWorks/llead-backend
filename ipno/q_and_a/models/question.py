from django.db import models

from martor.models import MartorField

from utils.models import TimeStampsModel


class Question(TimeStampsModel):
    question = models.TextField()
    answer = MartorField(blank=True, null=True)

    section = models.ForeignKey(
        "q_and_a.section", on_delete=models.CASCADE, related_name="questions"
    )
