import json
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

import pytz

from feedbacks.models import Feedback


class FeedbackViewSet(ViewSet):
    def create(self, request):
        feedback = json.loads(request.body)

        email = feedback.get("email")
        message = feedback.get("message")
        date_time = datetime.now(pytz.timezone("US/Central")).strftime(
            "%I:%M:%S%p %m/%d/%Y"
        )

        item = {
            "email": email,
            "message": message,
        }

        Feedback.objects.create(**item)

        context = {
            "message": (
                f"{message}\n\n"
                f"*Sent via contact form on [LLEAD.co](LLEAD.co) at {date_time}*"
            )
        }

        send_mail(
            subject="LLEAD.co Message",
            from_email=settings.FEEDBACK_TO_EMAIL,
            recipient_list=[settings.FEEDBACK_TO_EMAIL, email],
            html_message=render_to_string("email/dynamic_email.html", context),
            message=render_to_string("email/dynamic_email.html", context),
        )

        return Response({"detail": "Your message has been sent"})
