from django.conf import settings

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=settings.SLACK_BOT_TOKEN)


def notify_slack(message):
    try:
        client.chat_postMessage(channel=settings.SLACK_CHANNEL, text=message)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
