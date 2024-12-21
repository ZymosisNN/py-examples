from typing import Dict

from chatops_app.abstracts import ServiceResult, AbstractService
from chatops_app.services.slack import transport
from chatops_app.services.slack.slack_payloads import BaseSlackPayload


class SlackModalTransportSrv(AbstractService):
    def __init__(self, name: str, config: dict):
        super().__init__(name)
        self._token = config['SLACK_OATH_TOKEN']

    def exec(self, data: Dict) -> ServiceResult:
        """
        Mandatory data keys:
            'slack_payload' - SlackPayload, data for slack transport
            'view' - Slack modal view dict to be sent
        """
        payload: BaseSlackPayload = data['slack_payload']
        param = transport.SlackModalTransportParam(trigger_id=payload.trigger_id,
                                                   token=self._token,
                                                   response_url=payload.response_url)
        slack = transport.SlackModalTransport(param)
        res = slack.send_view(data['view'])
        return ServiceResult(service_name=self.name, error=None if res else 'Cannot open modal view')
