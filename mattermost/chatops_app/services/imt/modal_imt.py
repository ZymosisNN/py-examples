import json
from typing import Dict

from slack_sdk.models import blocks

from chatops_app.abstracts import ChatOpsError
from chatops_app.services import modal_write, modal_read
from chatops_app.services.imt.modal_assets_imt import COMMANDS, CMD_ARGS_MAP
from chatops_app.services.slack import slack_abstracts
from chatops_app.services.slack.slack_payloads import SlackModalPayload
from chatops_app.services.slack.srv_slack_transport import ALLOWED_CHANNEL_PREFIXES


class ModalLogicImt(slack_abstracts.AbstractModalLogic):
    def get_cmd_for_submit(self, payload: SlackModalPayload) -> str:
        state = payload.view['state']
        self.log_json(state, 'state:')

        self._log.debug('Parsed modal:')
        cmd = modal_read.get_value_for_key(state, 'cmd_selector')
        self._log.debug(f'    cmd = {cmd}')
        if not cmd:
            return ''

        args_list = []
        for arg in CMD_ARGS_MAP[cmd]:
            self._log.debug(f'    {arg}')
            arg_name = arg['name']
            value = modal_read.get_value_for_key(state, arg_name)
            text_key = arg.get('text_key')
            if arg['input_type'] == 'checkbox':
                if value:
                    args_list.append(text_key)
            else:
                if text_key:
                    args_list.append(text_key)
                if value is None:
                    self._log.error(f'{arg_name} is None!')
                    raise ChatOpsError('Slack modal submission data parse error! Please retry, verify entered data.')
                args_list.append(value)

        dest = modal_read.get_value_for_key(state, 'cmd_result_destination')
        if dest == 'send_to_channel':
            args_list.append('-all')

        metadata = json.loads(payload.view['private_metadata'])
        args_list.extend(['-dc', metadata['dc']])
        cmd_str = f'{cmd} {" ".join(args_list)}'
        self._log.debug(f'Generated cmd string: {cmd_str}')
        return cmd_str

    def build_modal_view(self, data: Dict) -> Dict:
        """
        Input data dict:
            'private_metadata'
            'view' (absent if initial modal)
            'actions' (absent if initial modal)
        """
        self.log_dict(data, 'Data to build modal view:')

        block_list = [
            blocks.SectionBlock(text='Please choose the IMT information type you would like to obtain'),
            modal_write.actions_static_select(block_id='cmd_selector',
                                              placeholder='Please select command',
                                              action_id='cmd_selected',
                                              options=[modal_write.option(text=i['title'], value=i['name'])
                                                       for i in COMMANDS])
        ]

        actions = data.get('actions')
        if actions:
            block_list.append(modal_write.DIVIDER)
            cmd = modal_read.find_by_key(actions, 'value')
            self._log.debug(f'Update view for cmd "{cmd}"')
            block_list.extend(modal_write.build_input_blocks(CMD_ARGS_MAP[cmd]))

        private_metadata = data['private_metadata']  # TODO: demand from data if new, but if modal then consider optional take from view

        if private_metadata['channel_name'].startswith(ALLOWED_CHANNEL_PREFIXES):
            block_list.append(modal_write.DIVIDER)
            block_list.append(modal_write.RESULT_DESTINATION_BLOCK)

        view = modal_write.build_view(title='IMT ChatOps Helper', block_list=block_list,
                                      private_metadata=private_metadata)

        existing_view = data.get('view')
        if existing_view:
            view.id = existing_view['id']

        # self.log_json(view.to_dict(), 'Created view:')
        return view.to_dict()
