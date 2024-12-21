import json
from pathlib import Path
from typing import List, Dict, NamedTuple

import requests
from slack_sdk.errors import SlackApiError
from slack_sdk.web import WebClient

from chatops_app.abstracts import LogMixin


class SlackTransportParam(NamedTuple):
    user_id: str
    channel_id: str
    channel_name: str
    response_url: str
    token: str


class SlackTransport(LogMixin):
    def __init__(self, param: SlackTransportParam):
        super().__init__()
        self.param = param
        self.slack_client = WebClient(param.token)

    def send_direct(self, text: str):
        return self._send_message(text, direct=True)

    def send_to_channel(self, text: str):
        return self._send_message(text, direct=False)

    def send_inside_thread(self, title_text: str, thread_text: str):
        res = self.send_to_channel_safe(title_text)
        try:
            thread_ts = res['message']['ts']
        except (KeyError, TypeError):
            self.send_ephemeral_to_response_url(
                'Sorry, but `-thread` option works only for the channels with ChatOps user added.')
            return self.send_ephemeral_to_response_url(thread_text)

        return self._send_message(thread_text, direct=False, thread_ts=thread_ts)

    def _send_message(self, text: str, direct: bool, thread_ts: str = None):
        self._log.info(f'Sending {"direct message" if direct else "to channel"}...')
        res = self.slack_client.chat_postMessage(user=self.param.user_id,
                                                 channel=self.param.user_id if direct else self.param.channel_id,
                                                 text=text,
                                                 thread_ts=thread_ts)
        self._log.info(res.status_code)
        return res

    def send_to_channel_safe(self, text: str):
        try:
            return self.send_to_channel(text)

        except SlackApiError as ex:
            if any(err in str(ex) for err in ('channel_not_found', 'invalid_channel', 'not_in_channel')):
                self._log.warning(f'ChatOps is not in the channel: (exception = {ex})')
                msg = ("*It seems that the ChatOps user hasn't been automatically added to this private channel, "
                       "so it's not allowed to use '-all' key here. Please add the ChatOps user to the channel "
                       "and retry the call*")
                return self.send_ephemeral_to_response_url(f'{msg}\n\n{text}')
            raise

    def send_to_response_url(self, text: str):
        return self._send_to_response_url(text, ephemeral=False)

    def send_ephemeral_to_response_url(self, text: str):
        return self._send_to_response_url(text, ephemeral=True)

    def _send_to_response_url(self, text: str, ephemeral: bool, attachments=''):
        self._log.info(f'Sending{" ephemeral " if ephemeral else " "}to response URL...')
        message = {'text': text,
                   'response_type': 'ephemeral' if ephemeral else 'in_channel',
                   'attachments': attachments}
        res = requests.post(self.param.response_url, json=message)
        self._log.info(res)
        return res

    def send_help(self, srv_description: str, command_list: List[Dict[str, str]]):
        attachments = [{
            'fallback': 'Required plain-text summary of the attachment.',
            'pretext': srv_description,
            'color': '#7000CC',
            'fields': [{'title': f"*{cmd['usage']}*", 'value': cmd['description']} for cmd in command_list]
        }]
        return self._send_to_response_url(text='', ephemeral=True, attachments=json.dumps(attachments))

    def send_file(self, filename: str, text: str, is_direct: bool):
        fname = Path(filename).name
        with open(filename, 'rb') as file:
            res = self.slack_client.files_upload(
                file=file,
                title=fname,
                filename=fname,
                initial_comment=text,
                channels=self.param.user_id if is_direct else self.param.channel_id
            )
            self._log.info(res)
            return res

    def send_snippet(self, snippet: Dict[str, str], is_direct: bool = False):
        self._log.info(f'Sending snippet {"directly" if is_direct else "to channel"}')
        res = self.slack_client.files_upload(
            content=snippet['content'],
            initial_comment=snippet.get('initial_comment'),
            title=snippet.get('title'),
            channels=self.param.user_id if is_direct else self.param.channel_id
        )
        self._log.info(res)
        return res


class SlackModalTransportParam(NamedTuple):
    token: str
    trigger_id: str
    response_url: str


class SlackModalTransport(LogMixin):
    INVALID_KEYS = ('id', 'team_id', 'state', 'hash', 'previous_view_id', 'root_view_id', 'app_id',
                    'app_installed_team_id', 'bot_id')

    def __init__(self, param: SlackModalTransportParam):
        super().__init__()
        self.param = param

    def send_view(self, view: Dict):
        view_id = view.get('id')

        self._log.debug(f'Remove from view: {self.INVALID_KEYS}')
        # views.update fails if next keys are present in view
        for key in self.INVALID_KEYS:
            view.pop(key, None)

        data = {'trigger_id': self.param.trigger_id,
                'token': self.param.token,
                'view': json.dumps(view)}

        if view_id:
            data['view_id'] = view_id
            res = requests.post('https://slack.com/api/views.update', data=data)

        else:
            res = requests.post('https://slack.com/api/views.open', data=data)

        return self._check_response(res)

    def _check_response(self, rsp) -> bool:
        self._log.info(rsp)
        content = rsp.json()
        if not content['ok']:
            self.log_json(content, 'Slack views open/update failed:')
            return False
        return True

    def send_ephemeral(self, text: str):
        self._log.info(f'Sending ephemeral to response URL...')
        message = {'text': text, 'response_type': 'ephemeral'}
        res = requests.post(self.param.response_url, json=message)
        self._log.info(res)
