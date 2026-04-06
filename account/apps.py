import os
from django.apps import AppConfig
from dotenv import load_dotenv

from django.conf import settings


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "account"
    path = os.path.dirname(os.path.abspath(__file__))

    def ready(self):
        load_dotenv()
        
        settings.AUTH_DEFAULT_HOME = os.getenv('AUTH_DEFAULT_HOME', 'account:index')
        settings.AUTH_EMAIL_AS_USERNAME = os.getenv('AUTH_EMAIL_AS_USERNAME', "False") == "True"
        settings.AUTH_DEFAULT_REDIRECT = os.getenv('AUTH_DEFAULT_REDIRECT', "account:index")
        settings.AUTH_BACKOFFICE = os.getenv('AUTH_BACKOFFICE', "False") == "True"
        settings.AUTH_SELF_CREATE = os.getenv('AUTH_SELF_CREATE', "False") == "True"
        settings.AUTH_SELF_RECOVERY = os.getenv('AUTH_SELF_RECOVERY', "False") == "True"
        settings.AUTH_AUTO_ACTIVATE = os.getenv('AUTH_AUTO_ACTIVATE', "False") == "True"
        settings.AUTH_TASK_TOKEN_LIFETIME = int(os.getenv('AUTH_TASK_TOKEN_LIFETIME', 60))
        settings.AUTH_GOOGLE_OAUTH_CLIENT_ID = os.getenv('AUTH_GOOGLE_OAUTH_CLIENT_ID', None)
        
        settings.USER_PAGINATION = os.getenv('USER_PAGINATION', 20)
        settings.USER_DEFAULT_HOME = os.getenv('USER_DEFAULT_HOME', None)

        settings.TEMPLATES[0]["OPTIONS"]["libraries"].update({
            "usertoolbar": "account.customtags.user",
            "user": "account.customtags.user",
        })