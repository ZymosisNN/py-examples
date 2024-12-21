from typing import Dict, Optional

from chatops_app.abstracts import ServiceResult, ContentType, AbstractService, ChatOpsError
from chatops_app.services.slack import transport
from chatops_app.services.slack.slack_msg_formatter import MessageFormatterImt
from chatops_app.services.slack.slack_payloads import BaseSlackPayload

ALLOWED_CHANNEL_PREFIXES = '_ta_', '_oa_', '_sa_', '_p1_', '_sec_', '_test_'


class SlackTransportSrvError(ChatOpsError):
    pass


class SlackTransportSrv(AbstractService):
    """
    Input
        data - dict:
            {'slackPayload': payload, 'content': ServiceResult}
    Output
        ServiceResult - OK/NOK
    """
    def __init__(self, name: str, config: dict):
        super().__init__(name)
        self._token = config['SLACK_OATH_TOKEN']

    def exec(self, data: Dict) -> ServiceResult:
        """
        Mandatory data keys:
            'slackPayload' - SlackPayload, data for slack transport
            'content' - ServiceResult, what to send via slack transport
        """
        payload: BaseSlackPayload = data['slack_payload']
        param = transport.SlackTransportParam(user_id=payload.user_id,
                                              channel_id=payload.channel_id,
                                              channel_name=payload.channel_name,
                                              response_url=payload.response_url,
                                              token=self._token)
        slack = transport.SlackTransport(param)

        # TODO: change from ServiceResult to specific data
        srv_result: ServiceResult = data['srv_result']

        if srv_result.content['cmd'] == 'help':
            slack.send_help(srv_result.content['srv_description'], srv_result.content['cmd_result'])
            return self.make_result()

        # TODO: add registration for formatters
        if srv_result.service_name == 'imt':
            return self._handle_result_imt(slack, srv_result, payload.user_name, payload.initial_command)

        if srv_result.service_name == 'lmw':
            return self._handle_result_lm(slack, srv_result, payload.user_name, payload.initial_command)

        if srv_result.service_name == 'mgr':
            return self._handle_result_mgr(slack, srv_result, payload.user_name, payload.initial_command)

        raise SlackTransportSrvError(f'Unknown service "{srv_result.service_name}"')

    # TODO: separate formatter from transport logic
    def _handle_result_imt(self, slack: transport.SlackTransport, srv_result: ServiceResult, username: str,
                           initial_command: str):
        cmd = srv_result.content['cmd']
        cmd_args = srv_result.content['cmd_args']
        cmd_result = srv_result.content['cmd_result']

        # If service returned nothing
        if not cmd_result:
            slack.send_ephemeral_to_response_url(
                f'Nothing has been found for your request: {initial_command}\n'
                'Please check if the parameters have been indicated correctly.'
            )
            return self.make_result()

        formatted_result = MessageFormatterImt(cmd, cmd_args).format(cmd_result)
        cmd_raw = initial_command or srv_result.content['cmd_raw']
        msg_title = f':white_check_mark: Result for *{username}*: {cmd_raw}'
        all_text = f'{msg_title}\n{formatted_result}'

        channel = slack.param.channel_name
        if cmd_args['all']:
            if channel == 'directmessage':
                slack.send_to_response_url(all_text)

            elif channel.startswith(ALLOWED_CHANNEL_PREFIXES):
                if cmd_args['thread']:
                    slack.send_inside_thread(msg_title, formatted_result)
                else:
                    slack.send_to_response_url(all_text)

            else:
                slack.send_ephemeral_to_response_url("Sorry, it's not allowed to use 'post in channel' option in "
                                                     f"'{channel}'.\n\n{all_text}")
        else:
            slack.send_ephemeral_to_response_url(all_text)

        return self.make_result()

    # TODO: this is MGR transport logic
    def _handle_result_mgr(self, slack: transport.SlackTransport, srv_result: ServiceResult, username: str,
                           initial_command: str):
        cmd_result = srv_result.content['cmd_result']
        cmd_raw = initial_command or srv_result.content['cmd_raw']
        msg_title = f'Result for *{username}*: {cmd_raw}'

        # TODO: need this check?
        if not cmd_result:
            slack.send_ephemeral_to_response_url(
                f'{msg_title}\nNothing has been found for your request.\n'
                'Please check if the parameters have been indicated correctly.'
            )
            return self.make_result()

        if isinstance(cmd_result, dict):
            slack.send_snippet({
                'content': cmd_result['body'],
                'initial_comment': f'{msg_title}\n{cmd_result["header"]}'
            })
        else:
            slack.send_ephemeral_to_response_url(f'{msg_title}\n{cmd_result}')

        return self.make_result()

    def _handle_result_lm(self, slack: transport.SlackTransport, srv_result: ServiceResult, username: str,
                          initial_command: str):
        if srv_result.content_type != ContentType.BINARY_FILEPATH:
            self._log.error(f'Content type from LM is not BINARY_FILEPATH ({srv_result.content_type})')

        cmd_raw = initial_command or srv_result.content['cmd_raw']
        slack.send_file(srv_result.content['file_path'],
                        text=f':white_check_mark: Result for *{username}*: {cmd_raw}',
                        is_direct=not srv_result.content['cmd_args']['all'])
        return self.make_result()

    def make_result(self, errmsg: Optional[str] = None):
        return ServiceResult(service_name=self.name, error=errmsg)
