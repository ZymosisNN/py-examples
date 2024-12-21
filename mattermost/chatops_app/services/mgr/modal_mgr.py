import re
from typing import Dict

from slack_sdk.models import blocks

from chatops_app.services import modal_write, modal_read
from chatops_app.services.mgr.modal_assets_mgr import ACTION_TO_COMMAND_MAP, INIT_CMD, NodeIds
from chatops_app.services.slack.slack_abstracts import AbstractModalLogic
from chatops_app.services.slack.slack_payloads import SlackModalPayload
from chatops_app.services.slack import slack_markdown as md

NO_QUEUES = '--- no open queues ---'


class ModalLogicMgr(AbstractModalLogic):
    def is_modal_opener(self, cmd: str) -> bool:
        return bool(re.match(r'request\b', cmd))

    def get_init_cmd(self) -> str:
        return INIT_CMD

    def get_cmd_for_action(self, payload: SlackModalPayload) -> str:
        action = modal_read.find_by_key(payload.actions, 'action_id')
        if action == NodeIds.QUEUE_SELECT:
            queue = modal_read.get_value_for_key(payload.view, NodeIds.QUEUE_SELECT)  # TODO: walrus
            if queue == NO_QUEUES:
                return ''
            cmd = f'{ACTION_TO_COMMAND_MAP[action]} {queue}'

        elif action == NodeIds.DOMAIN_INFO:
            domain_id = modal_read.get_value_for_key(payload.view, NodeIds.DOMAIN)  # TODO: walrus
            if not domain_id:
                return ''
            cmd = f'{ACTION_TO_COMMAND_MAP[action]} {domain_id}'

        else:
            return ''

        return f'{cmd} -dc {payload.dc}'

    def get_cmd_for_submit(self, payload: SlackModalPayload) -> str:
        queue = modal_read.get_value_for_key(payload.view, NodeIds.QUEUE_SELECT)
        if queue == NO_QUEUES:
            return ''
        domain_id = modal_read.get_value_for_key(payload.view, NodeIds.DOMAIN)
        return f'queue_domain_add -q "{queue}" -d {domain_id} -dc {payload.dc}'

    def build_modal_view(self, data: Dict) -> Dict:
        self.log_dict(data, 'Data to build modal view:')

        private_metadata = data['private_metadata']
        cmd_result = data.get('cmd_result', {})
        existing_view = data.get('view')

        if existing_view:
            self._log.debug('Reusing existing view values')
            current_queue = modal_read.get_value_for_key(existing_view, NodeIds.QUEUE_SELECT)
            chosen_queue = modal_write.option(text=current_queue, value=current_queue) if current_queue else None
            domain_id = modal_read.get_value_for_key(existing_view, NodeIds.DOMAIN)

            domain_info = cmd_result.get(NodeIds.DOMAIN_INFO)
            if domain_info is not None:  # TODO: walrus
                private_metadata['domain_info'] = str(
                    md.MD().key_value('Domain id', domain_info.get('domainId', 'NOT FOUND')).br()
                    .key_value('Domain name', domain_info.get('domain', 'NOT FOUND')).br()
                    .key_value('Current host', domain_info.get('currentHost', 'NOT FOUND')).br()
                )

            queue_info = cmd_result.get(NodeIds.QUEUE_SELECT)
            if queue_info:  # TODO: walrus
                private_metadata['queue_info'] = str(
                    md.MD().key_value('Direction', queue_info['direction']).br()
                    .key_value('Timer', queue_info['timer']).br()
                    .key_value('Opened by', queue_info['opened_by']).br()
                )

        else:
            queue_names = cmd_result.get(NodeIds.QUEUE_NAMES) or [NO_QUEUES]
            private_metadata['queue_options'] = [modal_write.option(text=i, value=i).to_dict() for i in queue_names]
            chosen_queue = domain_id = None

        block_list = [
            blocks.InputBlock(
                label='Please choose the queue to add domain to:',
                element=blocks.StaticSelectElement(action_id=NodeIds.QUEUE_SELECT,
                                                   options=private_metadata['queue_options'],
                                                   initial_option=chosen_queue,
                                                   placeholder=' '),
                dispatch_action=True
            ),
            blocks.SectionBlock(block_id=NodeIds.QUEUE_INFO,
                                text=blocks.MarkdownTextObject(text=private_metadata.get('queue_info', ' '))),
            modal_write.text_input(title='Domain ID:', value=NodeIds.DOMAIN, initial_value=domain_id),
            blocks.ActionsBlock(elements=[blocks.ButtonElement(text='Check domain', action_id=NodeIds.DOMAIN_INFO)]),
            blocks.SectionBlock(text=blocks.MarkdownTextObject(text=private_metadata.get('domain_info', ' '))),
        ]

        view = modal_write.build_view(title='MGR ChatOps Helper', block_list=block_list,
                                      private_metadata=private_metadata)

        if existing_view:
            view.id = existing_view['id']
            view.state = existing_view['state']

        # self.log_json(view.to_dict(), 'Created view:')
        return view.to_dict()
