import logging
from urllib.parse import parse_qs

from django import http
from django.conf import settings
from django.views.generic import View

from chatops_app import chatops_factory

CHATOPS = chatops_factory.get_chatops()


class SlackView(View):
    """ Handles both slash commands and modal Slack events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = logging.getLogger(self.__class__.__name__)
        self._slack_domain = settings.SLACK_CONFIG['SLACK_DOMAIN']

    def dispatch(self, request, *args, **kwargs):
        # Slack event verification
        mutual_tls_slack_meta = request.META.get('HTTP_X_CLIENT_CERTIFICATE_SAN', '')
        if self._slack_domain not in mutual_tls_slack_meta:
            self._log.error('Wrong or no "HTTP_X_CLIENT_CERTIFICATE_SAN" in the request')
            return http.HttpResponseBadRequest("'X-Slack-Domain' verification failed")

        return super().dispatch(request, *args, **kwargs)

    def post(self, request: http.HttpRequest):
        self._log.info('=' * 64)
        self._log.info(f'  NEW REQUEST: {request.path}')
        self._log.info('=' * 64)

        data = parse_qs(request.body.decode('utf-8'))
        rsp_data = CHATOPS.handle_slack_event(data)

        # TODO: add 3sec time check
        return http.JsonResponse(rsp_data) if rsp_data else http.HttpResponse()


def status(request):
    """ Network team asked for this """
    return http.HttpResponse('1')
