from django.conf import settings
from django.dispatch import receiver
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail

from app_config.models import AppTextContent


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    forgot_password_content = AppTextContent.objects.get(name='FORGOT_PASSWORD_EMAIL')
    message = forgot_password_content.value.replace('{HOST}', settings.HOST)\
        .replace('{reset_password_token}', reset_password_token.key)
    context = {"message": message}
    send_mail(
        subject="Password Reset",
        from_email=settings.FROM_EMAIL,
        recipient_list=[reset_password_token.user.email],
        html_message=render_to_string("email/dynamic_email.html", context),
        message=render_to_string("email/dynamic_email.html", context)
    )
