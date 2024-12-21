from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial
from typing import Dict, Callable

from chatops_app import sat_client
from chatops_app.abstracts import ContentType, ServiceResult, AbstractService, ChatOpsError
from chatops_app.services.command_str_parser import CmdStrParser, CmdStrParserError
from chatops_app.services.imt.imt_client import ImtClient, ImtClientError


class ImtCmdServiceError(ChatOpsError):
    pass


class ImtCmdService(AbstractService):
    SRV_DESCRIPTION = ('`/imt` or `/imteu` provides you the possibility to use IMT tools from Slack. '
                       # TODO:
                       # 'Default datacenter is US. '
                       # 'To define another one (EU or CA) you may use: `/imt <cmd> -dc eu` or `/imteu <cmd>`\n'
                       'By default, IMT slash commands will return result as a direct message to the person '
                       'who called the command.\n'
                       'To make the result to be sent in the channel directly add `-all` key to your request. '
                       'Currently it is allowed to use this key only in direct conversations or in the private '
                       'channels *if the ChatOps user is added to the channel*.')

    def __init__(self, name: str, imt_config: dict, sat_config: dict):
        super().__init__(name)
        self._cmd_method_map: Dict[str, Callable[[CmdStrParser, str], Dict]] = {
            'help': self._exec_help,
            'summary': self._exec_summary,
            'mgrstate': self._exec_mgrstate,
        }
        self._executor = ThreadPoolExecutor(imt_config['THREADS_COUNT'])
        self._imt_auth = imt_config['AUTH']['USER'], imt_config['AUTH']['PASSWORD']
        self._imt_urls = imt_config['URLS']
        self._sat_param = dict(
            auth=(sat_config['AUTH']['USER'], sat_config['AUTH']['PASSWORD']),
            req_interval=sat_config['API']['REQ_INTERVAL'],
            max_req_in_process=sat_config['API']['MAX_REQ_IN_PROCESS']
        )
        self.srv_result = partial(ServiceResult, service_name=self.name, content_type=ContentType.DICT)

    def exec(self, data: Dict) -> ServiceResult:
        """ data dict must contain a key 'cmd' - string command with arguments """
        cmd_str = data['cmd']
        dc = data['dc']
        try:
            parser = CmdStrParser(self.name, cmd_str)
            exec_func = self._cmd_method_map.get(parser.cmd, self._exec_other)
            cmd_result = exec_func(parser, dc)

        except (ImtCmdServiceError, CmdStrParserError, ImtClientError) as ex:
            self._log.error(ex)
            return self.srv_result(error=str(ex))

        # TODO: The value of chatops._default_dc should be here instead of 'us'
        srv_name = self.name if dc == 'us' else f'{self.name}{dc}'
        return self.srv_result(content={
            'cmd_raw': f'/{srv_name} {cmd_str}',
            'cmd': parser.cmd,
            'cmd_args': parser.args,
            **cmd_result
        })

    def _exec_help(self, parser, _):
        return {'cmd_result': parser.usage,
                'srv_description': self.SRV_DESCRIPTION}

    def _exec_summary(self, parser, dc):
        summary_future = self._make_task(self.imt_request, cmd='domain', cmd_args=parser.args, dc=dc)
        sessions_future = self._make_task(self.imt_request, cmd='jmx_sessions', cmd_args=parser.args, dc=dc)
        calls_future = self._make_task(self.imt_request, cmd='jmx_calls', cmd_args=parser.args, dc=dc)

        timeout = 10
        summary = summary_future.result(timeout)
        sessions = sessions_future.result(timeout)
        calls = calls_future.result(timeout)

        if not summary:
            return {'cmd_result': {}}

        return {'cmd_result': {'domain': summary, 'jmx_sessions': sessions, 'jmx_calls': calls}}

    def _exec_mgrstate(self, parser, dc):
        imt_result = self.imt_request('domain_verbose', parser.args, dc)
        if not imt_result:
            self._log.debug(f'IMT returned zero result for domain {parser.args["domain_id"]}')
            return {'cmd_result': []}

        providers = self.imt_request('providers', parser.args, dc)
        if not providers:
            self._log.debug(f'IMT returned zero result for providers in DC={dc}')
            return {'cmd_result': []}

        sat_url = sat_client.get_latest_sat_url(providers, dc)
        self._log.debug(f'SAT API URL: {sat_url}')
        with sat_client.SatClient(sat_url=sat_url, **self._sat_param) as sat:
            domain_state = sat.get_domains_state(parser.args['domain_id'])
        self.log_dict(domain_state, 'Domain state:')

        return {'cmd_result': [imt_result[0], domain_state]}

    def _exec_other(self, parser, dc):
        return {'cmd_result': self.imt_request(parser.cmd, parser.args, dc)}

    def imt_request(self, cmd, cmd_args, dc):
        dc = dc.upper()
        try:
            url = self._imt_urls[dc]
        except KeyError:
            raise ImtCmdServiceError(f'Unknown datacenter "{dc}"')
        imt_client = ImtClient(url=url, auth=self._imt_auth, cmd=cmd, cmd_args=cmd_args)
        result = imt_client.request()
        self.log_with_limit(result, 'IMT result:')
        return result

    def _make_task(self, func, *args, **kwargs) -> Future:
        self._log.debug('Starting a task thread')
        future = self._executor.submit(func, *args, **kwargs)

        def log_exceptions(done_future: Future):
            try:
                done_future.result()
            except Exception as ex:
                self._log.error(f'EXCEPTION in task thread: {ex}')
                raise ImtCmdServiceError(ex) from ex

        future.add_done_callback(log_exceptions)
        return future
