from typing import Dict

from slack_sdk.models import blocks

from chatops_app.services import modal_write, modal_read
from chatops_app.services.lm.modal_assets_lm import ACTION_TO_COMMAND_MAP, INIT_CMD, NodeIds
from chatops_app.services.slack.slack_abstracts import AbstractModalLogic
from chatops_app.services.slack.slack_payloads import SlackModalPayload


class ModalLogicLm(AbstractModalLogic):
    def get_init_cmd(self) -> str:
        return INIT_CMD

    def get_cmd_for_action(self, payload: SlackModalPayload) -> str:
        action = modal_read.find_by_key(payload.actions, 'action_id')
        value = modal_read.find_by_key(payload.actions, 'value')
        return f'{ACTION_TO_COMMAND_MAP[action]} "{value}"'

    def get_cmd_for_submit(self, payload: SlackModalPayload) -> str:
        view = payload.view
        dashboard = modal_read.get_value_for_key(view, NodeIds.DASHBOARD)
        widget = modal_read.get_value_for_key(view, NodeIds.WIDGET)
        tf = modal_read.get_value_for_key(view, NodeIds.TIMEFRAME)
        send_to = modal_read.get_value_for_key(view, 'cmd_result_destination')
        response_to_all = '-all' if send_to == 'send_to_channel' else ''

        return f'show -d {dashboard} -w {widget} -t {tf} {response_to_all}'

    def build_modal_view(self, data: Dict) -> Dict:
        """
        Input data dict:
            private_metadata
            dashboard_group_list - list of dashboard groups
            dashboard_list - list of dashboards
            widget_list - list of widgets
            state - dict, taken from existing view for update, absent if open new view
            viewId - str, taken from existing view for update, absent if open new view
        """
        self.log_dict(data, 'Data to build modal view:')

        existing_view = data.get('view')
        opt_groups = {}
        for opt_group in (NodeIds.DASHBOARD_GROUP, NodeIds.DASHBOARD, NodeIds.WIDGET):
            items = data.get(opt_group)
            if items:
                opt_groups[opt_group] = [modal_write.option(text=i, value=i) for i in items]
            elif not existing_view:
                self._log.debug(f'Using empty {opt_group}')
                opt_groups[opt_group] = [modal_write.option()]
            else:
                self._log.debug(f'Reusing existing {opt_group}')
                selector = modal_read.find_by_id(existing_view, opt_group)
                opt_groups[opt_group] = modal_read.find_by_key(selector, 'options')

        block_list = [
            modal_write.section_static_select(block_id=NodeIds.DASHBOARD_GROUP,
                                              title='Please choose the dashboard group you would like to get',
                                              action_id=NodeIds.DASHBOARD_GROUP,
                                              options=opt_groups[NodeIds.DASHBOARD_GROUP]),
            modal_write.section_static_select(block_id=NodeIds.DASHBOARD,
                                              title='Please choose the dashboard you would like to get',
                                              action_id=NodeIds.DASHBOARD,
                                              options=opt_groups[NodeIds.DASHBOARD]),
            modal_write.DIVIDER,
            blocks.InputBlock(
                label='Select the widget',
                element=blocks.StaticSelectElement(action_id=NodeIds.WIDGET,
                                                   options=opt_groups[NodeIds.WIDGET])
            ),
            blocks.InputBlock(
                label='Select the timeframe',
                element=blocks.StaticSelectElement(action_id=NodeIds.TIMEFRAME,
                                                   options=[modal_write.option(text=t, value=t)
                                                            for t in ('30m', '1h', '12h', '1d', '7d')])
            ),
        ]

        private_metadata = data['private_metadata']
        if private_metadata['channel_name'] != 'directmessage':
            block_list.append(modal_write.DIVIDER)
            block_list.append(modal_write.RESULT_DESTINATION_BLOCK)

        view = modal_write.build_view(title='LM ChatOps Helper', block_list=block_list,
                                      private_metadata=private_metadata)

        if existing_view:
            view.id = existing_view['id']
            view.state = existing_view['state']

        # self.log_json(view.to_dict(), 'Created view:')
        return view.to_dict()
