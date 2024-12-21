import json
import traceback
from typing import Dict, Any, Optional, Union, Tuple

import requests

from chatops_app.abstracts import LogMixin, ChatOpsError


class ImtClientError(ChatOpsError):
    pass


class ImtClient(LogMixin):
    BASE_IMT_DATA = {
        'domainName': '',
        'domainId': '',
        'accountName': '',
        'accountId': '',
        'mismatchOnly': False,
        'pdc_nvoip_farm_id': '',
        'bdc_nvoip_farm_id': '',
        'includePco': True,
        'smsEnabled': False,
        'phoneNum': '',
        'maxRows': 100,
        'includeDemo': False,
    }
    __CUST_INFO = 'GetCustInfoNew', 'CustDbInfo'
    __JMX_DATA = 'GetDomainJmxData', 'CustDbInfo'
    CMD_TO_PARAM_MAP = {
        'domain': __CUST_INFO,
        'domain_verbose': __CUST_INFO,
        'core': __CUST_INFO,
        'account': __CUST_INFO,
        'jmx_sessions': __JMX_DATA,
        'jmx_calls': __JMX_DATA,
        'fvs_provisioning': ('GetFvsDomainProvisioning', 'FvsDomainProvisioningInfo'),
        'domain_numbers': ('GetDomainPhoneNumber', 'DomainPhoneNum'),
        'jmx_domains': ('GetDomainJmxStatus', 'CustDbInfo'),
        'db': ('GetDbUsage', 'CustDbInfo'),
        'cnam': ('GetCnamChecker', 'CnamInfo'),
        'providers': ('GetAppData', ''),
    }

    def __init__(self, url: str, auth: Tuple[str, str], cmd: str, cmd_args: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.auth = auth
        self.cmd = cmd
        self.command_params = self.build_imt_req_data(cmd_args or {})

        try:
            # imt_result_type1 will be matched with IMT result JSON key "type1"
            endpoint, self.imt_result_type1 = self.CMD_TO_PARAM_MAP[self.cmd]
        except KeyError:
            raise ImtClientError(f'Command "{self.cmd}" is unimplemented')

        self.url = f'{url}/{endpoint}'

    def request(self) -> Union[list, dict]:
        try:
            response = requests.get(self.url, params=self.command_params, auth=self.auth, verify=False, timeout=10)
            response.raise_for_status()

        except requests.Timeout as ex:
            self._log.error(traceback.format_exc())
            raise ImtClientError('Sorry, IMT request reached timeout. Please retry it one more time') from ex

        except requests.RequestException as ex:
            self._log.error(traceback.format_exc())
            raise ImtClientError('Request to IMT failed') from ex

        result = response.text
        self.log_with_limit(result, f'{"< BEGIN IMT response >":-^64}')
        self._log.debug(f'{"< END IMT response >":-^64}')

        return self.parse_result(result)

    def parse_result(self, response: str) -> Union[list, dict]:
        result = json.loads(response.replace('\xfa', ''))
        if self.cmd in ('jmx_domains', 'providers', 'cnam'):
            return result

        if self.cmd in ('jmx_calls', 'jmx_sessions'):
            try:
                return [i.replace('\r', '')
                        for item in result if item['type1'] == 'JmxData'
                        for i in item['data'].split('\n') if '=' in i or ':' in i]
            except KeyError:
                raise ImtClientError('Cannot parse IMT result!')

        elif self.cmd == 'db':
            req_db_server_dict = None
            db_gr_details = {}
            req_db_hostname = self.command_params['ipAddress']
            needed_keys = 'domain', 'domainId', 'dbHostCurrent', 'slaveDbHostCurrent', 'dsName', 'dbName', 'currentHost'
            domains = []

            for item in result:
                if item['type1'] == 'DbServerInfo':
                    if req_db_hostname in item['dbHost']:
                        req_db_server_dict = item
                    db_gr_details[f"{item['dbHost'].split('.')[1].upper()} {item['dbRole']}"] = item['dbHost']

                elif item['type1'] == 'CustDbInfo':
                    domains.append({key: item.get(key) for key in needed_keys})

            if not req_db_server_dict:
                raise ImtClientError(f'No requested "{req_db_hostname}" in IMT result')

            db_usage = {
                'requested_db_server': req_db_server_dict,
                'domains': domains,
                'db_gr_details': db_gr_details
            }
            return db_usage

        else:
            self._log.debug('Default IMT result parsing for basic IMT commands: '
                            'domain, domain_verbose, core, account, summary, domain_numbers, mgrstate')
            return [item for item in result if item['type1'] == self.imt_result_type1]

    def build_imt_req_data(self, cmd_params: Dict[str, Any]):
        cmd_data = self.BASE_IMT_DATA.copy()
        cmd_data['domainId'] = cmd_params.get('domain_id', '')

        if 'name_or_id' in cmd_params:
            item_id = item_name = ''
            try:
                item_id = int(cmd_params['name_or_id'])
            except ValueError:
                item_name = cmd_params['name_or_id']

            if self.cmd == 'account':
                cmd_data['accountId'] = item_id
                cmd_data['accountName'] = item_name
            else:
                cmd_data['domainId'] = item_id
                cmd_data['domainName'] = item_name

        if self.cmd == 'jmx_sessions':
            cmd_data['type'] = 'sessions'
        if self.cmd == 'jmx_calls':
            cmd_data['type'] = 'calls'

        if self.cmd == 'db':
            cmd_data['ipAddress'] = cmd_params['db_host']
            cmd_data['includeDemo'] = True

        if self.cmd in ('domain', 'domain_verbose', 'account', 'summary', 'mgrstate'):
            cmd_data['includeDemo'] = True
            cmd_data['maxRows'] = 1000

        if self.cmd == 'providers':
            cmd_data['params'] = 'providers'

        if self.cmd == 'core':
            cmd_data['currentHost'] = cmd_params['core_host']

        if self.cmd == 'jmx_domains':
            cmd_data['domainHost'] = cmd_params['core_host']

        if self.cmd == 'cnam':
            cmd_data['provider'] = 'twilio,opencnam'
            cmd_data['numbers'] = ','.join(cmd_params['phone_numbers'])
            cmd_data['authToken'] = cmd_params['token']

        self.log_dict(cmd_data, 'DATA FOR IMT:')
        return cmd_data
