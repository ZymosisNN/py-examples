import json
import logging
import re
import traceback
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from typing import Dict, Tuple, Union

from chatops_app import storage
from chatops_app.abstracts import ChatOpsError, LogMixin, ServiceRequest, ServiceResult
from chatops_app.service_manager import ServiceManager
from chatops_app.services.slack import transport
from chatops_app.services.slack.slack_abstracts import AbstractModalLogic
from chatops_app.services.slack.slack_payloads import SlackPayload, SlackModalPayload, BaseSlackPayload


class ChatOps(LogMixin):
    def __init__(self, token: str, threads_count: int, service_manager: ServiceManager, default_dc: str):
        super().__init__()
        self._modal_logics: Dict[str, AbstractModalLogic] = {}
        self._token = token
        self._executor = ThreadPoolExecutor(max_workers=threads_count)
        self._srv_manager = service_manager
        self._default_dc = default_dc
        self._users_data = logging.getLogger('users_data')

    def register_modal_logic(self, logic: AbstractModalLogic):
        if logic.name in self._modal_logics:
            raise ChatOpsError(f'ModalLogic for service "{logic.name}" has already been registered')
        self._modal_logics[logic.name] = logic
        self._log.debug(f'ModalLogic for service "{logic.name}" registered')

    def get_modal_logic(self, service_name: str):
        try:
            return self._modal_logics[service_name]
        except KeyError:
            raise ChatOpsError(f'ModalLogic for service "{service_name}" is not registered')

    def handle_slack_event(self, data: Dict) -> Dict:
        """
        Takes slack event dict from http request
        Returns dict of data to be returned in http response to slack in 3 seconds
        """
        if 'command' in data:
            payload = self.convert_to_slack_payload(data)
            self._log_dicts_no_view({'Raw Slack event:': data, 'Payload:': payload.__dict__})
            if not self._check_permissions(payload):
                return {'text': f':x: User *{payload.user_name}* is not authorised to use */{payload.command}*'}
            self._make_task(self._process_slash_cmd, payload=payload)
            return {'text': payload.initial_command}

        else:
            data = json.loads(data['payload'][0])
            payload = self.convert_to_slack_modal_payload(data)
            self._log_dicts_no_view({'Raw Slack modal event:': data, 'Payload:': payload.__dict__})
            self._make_task(self._process_modal, payload=payload)
            return {}

    def _log_dicts_no_view(self, dicts_to_log: Dict[str, Dict]):
        """ Logs sorted dicts with substituting stub for view value """
        for description, dict_to_log in dicts_to_log.items():
            no_view = {k: ('{...too big for logs...}' if k == 'view' else v) for k, v in sorted(dict_to_log.items())}
            self.log_dict(no_view, description)

    def _process_slash_cmd(self, payload: SlackPayload):
        # This call will raise exception if modal logic is not registered
        # Leave it as it is until we have services without modals
        modal_logic = self.get_modal_logic(payload.command)

        if modal_logic.is_modal_opener(payload.text):
            self._exec_srv_cmd_and_handle_modal(cmd=modal_logic.get_init_cmd(), payload=payload)
        else:
            self._exec_srv_cmd_and_respond(cmd=payload.text, payload=payload)

    def _process_modal(self, payload: SlackModalPayload):
        modal_logic = self.get_modal_logic(payload.command)
        if payload.event_type == 'view_submission':
            cmd = modal_logic.get_cmd_for_submit(payload)
            if cmd:  # TODO: walrus to be here when we have Python >=3.8
                self._exec_srv_cmd_and_respond(cmd=cmd, payload=payload)
            else:
                slack = self._get_msg_transport(payload)
                slack.send_ephemeral_to_response_url('Nothing selected')
        else:
            self._exec_srv_cmd_and_handle_modal(cmd=modal_logic.get_cmd_for_action(payload), payload=payload)

    def _exec_srv_cmd_and_respond(self, cmd: str, payload: BaseSlackPayload):
        srv_result = self._exec_srv_cmd(srv_name=payload.command, data={'cmd': cmd, 'slack_payload': payload})
        self._exec_srv_cmd(srv_name='slack_msg_transport',
                           data={'slack_payload': payload, 'srv_result': srv_result})

    def _exec_srv_cmd_and_handle_modal(self, cmd: str, payload: Union[SlackPayload, SlackModalPayload]):
        data_for_modal = {'private_metadata': payload.make_private_metadata()}

        if isinstance(payload, SlackModalPayload):
            data_for_modal['actions'] = payload.actions
            data_for_modal['view'] = payload.view

        if cmd:
            srv_result = self._exec_srv_cmd(srv_name=payload.command, data={'cmd': cmd, 'slack_payload': payload})
            data_for_modal.update(srv_result.content)

        view = self.get_modal_logic(payload.command).build_modal_view(data_for_modal)
        self._exec_srv_cmd(srv_name='slack_modal_transport',
                           data={'slack_payload': payload, 'view': view})

    def _exec_srv_cmd(self, srv_name: str, data: Dict) -> ServiceResult:
        log_data = f', cmd="{data["cmd"]}"' if 'cmd' in data else ''
        self._log.info(f'Execute request: service="{srv_name}"{log_data}')
        slack_payload = data['slack_payload']
        srv_result = self._srv_manager.request(ServiceRequest(service_name=srv_name,
                                                              data={**data, 'dc': slack_payload.dc}))
        if srv_result.error:
            msg = f'Service "{srv_result.service_name}" failed: {srv_result.error}'
            self._log.error(msg)
            slack = self._get_msg_transport(slack_payload)
            slack.send_ephemeral_to_response_url(f':x: {msg}')
            raise ChatOpsError(msg)

        return srv_result

    def _get_msg_transport(self, payload):
        param = transport.SlackTransportParam(user_id=payload.user_id,
                                              channel_id=payload.channel_id,
                                              channel_name=payload.channel_name,
                                              response_url=payload.response_url,
                                              token=self._token)
        return transport.SlackTransport(param)

    def convert_to_slack_payload(self, data: Dict):
        cmd = data['command'][0]
        text = data.get('text', ['help'])[0]
        initial_command = f'{cmd} {text}'
        cmd, text, dc = self._normalize_dc_in_slash_cmd(cmd=cmd.lstrip('/'), text=text)
        return SlackPayload(
            user_id=data['user_id'][0],
            user_name=data['user_name'][0],
            command=cmd,
            channel_id=data['channel_id'][0],
            channel_name=data['channel_name'][0],
            trigger_id=data['trigger_id'][0],
            response_url=data['response_url'][0],
            text=text,
            token=data['token'][0],
            api_app_id=data['api_app_id'][0],
            dc=dc,
            initial_command=initial_command
        )

    def _normalize_dc_in_slash_cmd(self, cmd: str, text: str) -> Tuple[str, str, str]:
        """
        Cut DC off the command or fetch it from text. If not found, take default DC.
        @param cmd: slash command
        @param text: command text
        @return: tuple: cmd , text, dc
        """
        match = re.search(r'(imt)(eu|ca)', cmd)
        if match:
            cmd, dc = match.groups()
        else:
            match = re.search(r'-dc +(\w+)', text)
            dc = match.group(1).lower() if match else self._default_dc

        text = re.sub(r'-dc +\w+', '', text)
        return cmd, text, dc

    @staticmethod
    def convert_to_slack_modal_payload(data: Dict):
        view = data['view']
        private_metadata = json.loads(view['private_metadata'])
        return SlackModalPayload(
            command=private_metadata['command'],
            channel_id=private_metadata['channel_id'],
            channel_name=private_metadata['channel_name'],
            response_url=private_metadata['response_url'],
            dc=private_metadata['dc'],
            event_type=data['type'],
            user_id=data['user']['id'],
            user_name=data['user']['username'],
            api_app_id=data['api_app_id'],
            token=data['token'],
            trigger_id=data['trigger_id'],
            view=view,
            actions=data.get('actions', [{}])[0],
            initial_command='',
            private_metadata=private_metadata
        )

    def _make_task(self, func, **kwargs) -> Future:
        self._log.debug('Starting a task thread')
        future = self._executor.submit(func, **kwargs)

        def log_exceptions(done_future: Future):
            try:
                done_future.result()

            # For predictable errors
            except ChatOpsError as ex:
                self._log.error(f'EXCEPTION in task thread: {ex}')
                raise

            # For WTFs
            except Exception as ex:
                self._log.critical(f'ROYAL CLUSTERFUCK: {ex}\n{traceback.format_exc()}')
                slack = self._get_msg_transport(payload=kwargs['payload'])
                # TODO: add mail notification about exceptions here!
                slack.send_ephemeral_to_response_url('Server exception, please contact Tools Team')
                raise

        future.add_done_callback(log_exceptions)
        return future

    def _check_permissions(self, payload: SlackPayload):
        self._log.info('Checking user permissions to run the command...')
        cmd_allowed_groups = storage.get_cmd_permissions(payload.command)
        userdata = storage.get_user_data(payload.user_id)
        usergroups = userdata['usergroups']
        allowed_commands = userdata['allowed_commands']

        self.log_dict({
            'User name': payload.user_name,
            'User allowed commands': allowed_commands,
            'Command': payload.command,
            'User groups': usergroups,
            'Command allowed groups': cmd_allowed_groups,
        })

        permitted = payload.command in allowed_commands or any(ug for ug in usergroups if ug in cmd_allowed_groups)
        self._log.info(f'Permitted: {permitted}')
        self._log_user_data(payload=payload, permitted=permitted, usergroups=usergroups)
        return permitted

    def _log_user_data(self, payload: SlackPayload, permitted, usergroups):
        """
        Builds JSON string user data for report to ElasticSearch
        """
        msg = json.dumps({
            'Timestamp': datetime.utcnow().isoformat(sep=' ', timespec='milliseconds'),
            'user': payload.user_name,
            'user_groups': ','.join(usergroups),
            'command_type': f'/{payload.command}',
            'command': payload.text.split()[0],
            'permitted': permitted,
        })
        self._users_data.info(msg)
