from django.conf import settings

import structlog
from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox.dropbox_client import Dropbox

logger = structlog.get_logger("IPNO")


class DropboxService:
    def __init__(self):
        dropbox_refresh_token = settings.DROPBOX_REFRESH_TOKEN

        if not dropbox_refresh_token:
            raise ValueError("No dropbox refresh token found, please init it first")

        dropbox_client = Dropbox(
            oauth2_refresh_token=dropbox_refresh_token,
            app_key=settings.DROPBOX_APP_KEY,
            app_secret=settings.DROPBOX_APP_SECRET,
        )

        self.dropbox_client = dropbox_client

    @staticmethod
    def generate_dropbox_token():
        auth_flow = DropboxOAuth2FlowNoRedirect(
            settings.DROPBOX_APP_KEY,
            settings.DROPBOX_APP_SECRET,
            token_access_type="offline",
        )
        authorize_url = auth_flow.start()
        logger.info("1. Go to: " + authorize_url)
        logger.info('2. Click "Allow" (you might have to log in first).')
        logger.info("3. Copy the authorization code.")
        auth_code = input("Enter the authorization code here: ").strip()

        oauth_result = auth_flow.finish(auth_code)
        refresh_token = oauth_result.refresh_token

        logger.info(
            "Here is your refresh_token, please save it to your config."
            f" ${refresh_token}"
        )

    def get_temporary_link_from_path(self, path):
        self.dropbox_client.check_and_refresh_access_token()
        return self.dropbox_client.files_get_temporary_link(path).link
