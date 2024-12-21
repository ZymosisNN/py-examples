from functools import partial
from typing import Dict, Callable

from chatops_app.abstracts import AbstractService, ChatOpsError, ServiceResult, ContentType
from chatops_app.services.command_str_parser import CmdStrParser, CmdStrParserError
from chatops_app.services.lm.lm_client import LmClient, LmClientError
from chatops_app.services.lm.modal_assets_lm import NodeIds


class LmCmdServiceError(ChatOpsError):
    pass


class LmCmdService(AbstractService):
    SRV_DESCRIPTION = ('`/lmw` provides you the possibility to obtain LogicMonitor widgets from Slack.\n'
                       'By default, LM slash commands will return result as a direct message to the person '
                       'who called the command.\n'
                       'To make the result to be sent in the channel directly add `-all` key to your request. '
                       'Currently it is allowed to use this key only in direct conversations or in the private '
                       'channels *if the ChatOps user is added to the channel*.')

    def __init__(self, name: str, config: dict, widgets_filepath: str):
        super().__init__(name)
        self._config = config
        self._widgets_filepath = widgets_filepath
        self._cmd_method_map: Dict[str, Callable[[LmClient, CmdStrParser, Dict], ServiceResult]] = {
            'help': self._exec_help,
            'get_dashboard_groups': self._exec_get_dashboard_groups,
            'get_dashboards': self._exec_get_dashboards,
            'get_widgets': self._exec_get_widgets,
        }
        self.srv_result = partial(ServiceResult, service_name=self.name)

    def exec(self, data: Dict) -> ServiceResult:
        """ data dict must contain a key 'cmd' - string command with arguments """
        cmd_str = data['cmd']
        try:
            parser = CmdStrParser(self.name, cmd_str)
        except CmdStrParserError as ex:
            self._log.error(ex)
            return self.srv_result(error=f'Error during "{cmd_str}" parsing: {ex}')

        result_content = {'cmd_raw': f'/{self.name} {cmd_str}', 'cmd': parser.cmd, 'cmd_args': parser.args,
                          'cmd_result': None}
        client = LmClient(params=parser.args, config=self._config, widgets_filepath=self._widgets_filepath)

        exec_func = self._cmd_method_map.get(parser.cmd, self._exec_other)
        return exec_func(client, parser, result_content)

    def _exec_help(self, _, parser, result_content):
        result_content['cmd_result'] = parser.usage
        result_content['srv_description'] = self.SRV_DESCRIPTION
        return self.srv_result(content=result_content, content_type=ContentType.DICT)

    def _exec_get_dashboard_groups(self, client, _, result_content):
        result_content[NodeIds.DASHBOARD_GROUP] = client.get_dashboard_groups()
        return self.srv_result(content=result_content, content_type=ContentType.DICT)

    def _exec_get_dashboards(self, client, parser, result_content):
        result_content[NodeIds.DASHBOARD] = client.get_dashboards(parser.args['dashboard_group'])
        return self.srv_result(content=result_content, content_type=ContentType.DICT)

    def _exec_get_widgets(self, client, parser, result_content):
        result_content[NodeIds.WIDGET] = client.get_widgets(parser.args['dashboard'])
        return self.srv_result(content=result_content, content_type=ContentType.DICT)

    def _exec_other(self, client, parser, result_content):
        try:
            filename = client.get_widget_image()
        except LmClientError as ex:
            self._log.error(ex)
            return self.srv_result(error=f'Error during "{parser.cmd}" execution: {ex}')

        self._log.info(f'LM output path: {filename}')
        result_content['file_path'] = filename
        return self.srv_result(content=result_content, content_type=ContentType.BINARY_FILEPATH)  # TODO wrong type actually
