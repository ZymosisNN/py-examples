from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial
from typing import Dict, Callable

from chatops_app import sat_client
from chatops_app import storage
from chatops_app.abstracts import ContentType, ServiceResult, AbstractService, ChatOpsError
from chatops_app.services.command_str_parser import CmdStrParser, CmdStrParserError
from chatops_app.services.imt.imt_client import ImtClient
from chatops_app.services.mgr.modal_assets_mgr import NodeIds
from chatops_app.services.slack import slack_markdown as md
from chatops_app.services.slack.slack_payloads import BaseSlackPayload
from . import msg_formatter

TIMESTAMP_FMT = '%d %b %Y %H:%M:%S'


class MgrCmdServiceError(ChatOpsError):
    pass


class MgrCmdService(AbstractService):
    SRV_DESCRIPTION = ('`/mgr` command assists with CS requests for MGR functionality - i.e. provides the option '
                       'to form MGR queues, request the domains addition to the queues as well as indicate that '
                       'the domain from the queue has been processed. Please check the information below to see '
                       'how `/mgr` slash command works')

    def __init__(self, name: str, mgr_config: dict, imt_config: dict, sat_config: dict):
        super().__init__(name)
        self._cmd_method_map: Dict[str, Callable[[CmdStrParser, str], ...]] = {
            'help': self._exec_help,
            'queue_add': self._exec_queue_add,
            'queue_close': self._exec_queue_close,
            'queue_list': self._exec_queue_list,
            'queue_status': self._exec_queue_status,
            'queue_domain_add': self._exec_queue_domain_add,
            'queue_pull': self._exec_queue_pull,
            'queue_pull_all': self._exec_queue_pull,
            'get_queues': self._exec_get_queues,
            'get_queue_info': self._exec_get_queue_info,
            'get_domain_info': self._exec_get_domain_info,
        }
        self._executor = ThreadPoolExecutor(mgr_config['THREADS_COUNT'])
        self._imt_auth = imt_config['AUTH']['USER'], imt_config['AUTH']['PASSWORD']
        self._imt_urls = imt_config['URLS']
        self._sat_param = dict(
            auth=(sat_config['AUTH']['USER'], sat_config['AUTH']['PASSWORD']),
            req_interval=sat_config['API']['REQ_INTERVAL'],
            max_req_in_process=sat_config['API']['MAX_REQ_IN_PROCESS']
        )
        self.srv_result = partial(ServiceResult, service_name=self.name, content_type=ContentType.DICT)

    def exec(self, data: Dict) -> ServiceResult:
        cmd_str = data['cmd']
        try:
            parser = CmdStrParser(self.name, cmd_str)
        except CmdStrParserError as ex:
            self._log.error(ex)
            return self.srv_result(error=f'Parse error "{cmd_str}": {ex}')

        exec_func = self._cmd_method_map.get(parser.cmd, self._exec_help)
        payload: BaseSlackPayload = data['slack_payload']
        try:
            cmd_result = exec_func(parser, payload.user_id)
        except ChatOpsError as ex:
            self._log.error(ex)
            return self.srv_result(error=f'Execution error "{parser.cmd}": {ex}')

        content = {'cmd_raw': f'/{self.name} {cmd_str}', 'cmd': parser.cmd, 'cmd_args': parser.args,
                   'cmd_result': cmd_result, 'srv_description': self.SRV_DESCRIPTION}
        return self.srv_result(content=content)

    def _exec_queue_add(self, parser: CmdStrParser, slack_user_id: str):
        qname = parser.args['queue_name']
        try:
            storage.add_mgr_queue(
                name=qname,
                direction=parser.args['direction'],
                timer=parser.args['timer'],
                slack_user_id=slack_user_id
            )
        except storage.ObjectAlreadyExists:
            return md.nok(f'Open queue with name "{qname}" already exists')

        return md.ok(f'Queue "{qname}" added')

    def _exec_queue_close(self, parser: CmdStrParser, slack_user_id: str):
        qname = parser.args['queue_name']
        try:
            storage.close_mgr_queue(name=qname, slack_user_id=slack_user_id)
        except (storage.ObjectDoesNotExist, storage.ObjectAlreadyExists) as e:
            return md.nok(e)

        return md.ok(f'Queue "{qname}" closed')

    def _exec_queue_list(self, parser: CmdStrParser, _):
        state_str = 'Closed' if parser.args['closed'] else 'Open'
        queues = storage.get_mgr_queues(closed=parser.args['closed'])
        if not queues:
            return md.ok(f'No {state_str} MGR queues')

        return msg_formatter.format_queue_list(queues)

    def _exec_queue_status(self, parser: CmdStrParser, _):
        qname = parser.args['queue_name']
        try:
            queue, domains = storage.get_mgr_queue_status(name=qname)
        except storage.ObjectDoesNotExist as e:
            return md.nok(e)

        # TODO: some double code from imt service
        providers = self.imt_request('providers', parser.args)
        if not providers:
            self._log.debug(f'IMT returned zero result for providers in DC={parser.args["dc"]}')
            return {'cmd_result': []}

        sat_url = sat_client.get_latest_sat_url(providers, parser.args['dc'])
        self._log.debug(f'SAT API URL: {sat_url}')

        timeout = 10
        with sat_client.SatClient(sat_url=sat_url, **self._sat_param) as sat:
            futures = {self._make_task(sat.get_domains_state, domain_id=domain['domain_id']): domain
                       for domain in domains}
            for future, domain in futures.items():
                try:
                    domain_state = future.result(timeout)
                    self.log_dict(domain_state, 'Domain state:')
                    domain['mgr_state'] = domain_state['migration']['status']['state']

                except Exception as e:
                    self._log.exception(e)
                    domain['mgr_state'] = 'UNKNOWN'

                self.log_dict(domain, 'DOMAIN:')

        formatted = msg_formatter.format_queue_status(queue, domains)
        if isinstance(formatted, tuple):
            return {'header': formatted[0], 'body': formatted[1]}

        return formatted

    def _exec_queue_domain_add(self, parser: CmdStrParser, slack_user_id: str):
        domain_id = parser.args['domain_id']
        domain_info = self._get_domain(domain_id, parser.args['dc'])
        if not domain_info:
            return md.nok(f'Domain with ID={domain_id} not found')
        try:
            storage.add_mgr_domain(qname=parser.args['queue_name'], domain_id=domain_id,
                                   domain_name=domain_info['domain'], slack_user_id=slack_user_id)
        except storage.ObjectAlreadyExists as e:
            return md.nok(e)

        return md.ok(f'Domain "{domain_id}" added')

    def _exec_queue_pull(self, parser: CmdStrParser, slack_user_id: str):
        qname = parser.args['queue_name']
        ids = parser.args.get('domain_ids')
        try:
            pulled_ids = storage.pull_domains(qname=qname, slack_user_id=slack_user_id, domain_ids=ids)
        except storage.ObjectDoesNotExist as e:
            return md.nok(e)

        self._log.debug(f'Pulled domains: {pulled_ids}')
        ids_str = ';'.join(str(i) for i in pulled_ids)
        return md.ok(f'Domains {ids_str} from queue "{qname}" are processed by you')

    def _exec_get_queues(self, _, __):
        queues = storage.get_mgr_queues(closed=False)
        return {NodeIds.QUEUE_NAMES: [queue['name'] for queue in queues]}

    def _exec_get_queue_info(self, parser: CmdStrParser, _):
        queues = storage.get_mgr_queues(closed=False)
        for queue in queues:
            if queue['name'] == parser.args['queue_name']:
                return {NodeIds.QUEUE_SELECT: queue}
        return {NodeIds.QUEUE_SELECT: {}}

    def _exec_get_domain_info(self, parser: CmdStrParser, _):
        domain_info = self._get_domain(domain_id=parser.args['domain_id'], dc=parser.args['dc'])
        return {NodeIds.DOMAIN_INFO: domain_info}

    def _exec_help(self, parser: CmdStrParser, _):
        return parser.usage

    def _get_domain(self, domain_id: int, dc: str) -> Dict:
        self._log.debug(f'Get domain (id={domain_id}) info via IMT')
        result = self.imt_request(cmd='domain', cmd_args={'domain_id': domain_id, 'dc': dc})
        return result[0] if result else {}

    def imt_request(self, cmd: str, cmd_args: Dict):
        url = self._imt_urls[cmd_args['dc'].upper()]
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
                raise MgrCmdServiceError(ex) from ex

        future.add_done_callback(log_exceptions)
        return future
