import urllib3
from django.apps import AppConfig


class ChatopsConfig(AppConfig):
    name = 'chatops_app'
    verbose_name = "Chat Ops"

    def ready(self):
        urllib3.disable_warnings()
