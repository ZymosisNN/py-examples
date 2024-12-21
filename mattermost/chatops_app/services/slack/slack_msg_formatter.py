import traceback
from datetime import datetime
from typing import Any, Dict, List, Callable, Union, Sequence

from chatops_app.abstracts import LogMixin


class MessageFormatterImt(LogMixin):
    """
    Slack format:
        Hyperlink: <https://some.url|"How it's shown in message">
        Bold: *bold text*
        Italic: _italic text_
        Strike: ~strike text~
        Mono: `mono text`
        Code block: ```code block text```
        Quote: >quoted text
    """
    MAX_DOMAIN_NUMBERS = 200
    RESULT_DICTIONARY_NAMES = {
        'account': {'farmName': 'Freedom Farm', 'accountName': 'Account Name', 'dbName': 'DB Name', 'mmHost': 'MM Host', 'ext_nsp_agents': 'NetSuite+  Agents', 'acBoards': 'AC Boards', 'bkupHost': 'Backup Host', 'currentHost': 'Current Host', 'allDay': '24/7', 'ext_adtp_agents': 'ADT+ Agents', 'ext_orp_agents': 'Oracle+ Agents', 'ext_inbound_lines': 'Inbound lines', 'ext_outbound_lines': 'Outbound lines', 'domainHost': 'Primary Host', 'ext_msdp_agents': 'MS Dynamics+ Agents', 'ext_zdp_agents': 'Zendesk+ Agents', 'sipTrunks': 'SIP Trunks', 'dynamicFtp': 'Dynamic FTP', 'loopback': 'Loopback', 'ext_recordings': 'Recordings', 'fvs': 'FVS', 'dsName': 'DS Name', 'partitionId': 'Partition ID', 'ftpServer': 'FTP Server', 'w2c': 'W2C', 'dbHost': 'DB host', 'verint_packages': 'Verint packages', 'domainId': 'Domain ID', 'accountId': 'Account ID', 'sccDomainId': 'SCC Domain ID', 'immediate': 'Immediate', 'domain': 'Domain Name', 'agentCount': 'Agents Count', 'ext_max_conference': 'Max Conference', 'nvoipPdcFarmName': 'NVOIP PDC Farm Name', 'nvoipBdcFarmName': 'NVOIP BDC Farm Name', 'nvoipFarmName': 'Current NVOIP Farm', 'primaryHostNas': 'PDC NAS', 'backupHostNas': 'BDC NAS', 'partitionCodec': 'Domain Codec'},
        'domain': {'accountName': 'Account', 'dbName': 'Current DB', 'currentHost': 'Current Host', 'domain': 'Domain', 'provider_name': 'Provider Name'},
        'domain_verbose': {'farmName': 'Freedom Farm', 'accountName': 'Account Name', 'dbName': 'DB Name', 'provider_name': 'Provider Name', 'mmHost': 'MM Host', 'ext_nsp_agents': 'NetSuite+  Agents', 'acBoards': 'AC Boards', 'bkupHost': 'Backup Host', 'currentHost': 'Current Host', 'allDay': '24/7', 'ext_adtp_agents': 'ADT+ Agents', 'ext_orp_agents': 'Oracle+ Agents', 'ext_inbound_lines': 'Inbound lines', 'ext_outbound_lines': 'Outbound lines', 'domainHost': 'Primary Host', 'ext_msdp_agents': 'MS Dynamics+ Agents', 'ext_zdp_agents': 'Zendesk+ Agents', 'sipTrunks': 'SIP Trunks', 'dynamicFtp': 'Dynamic FTP', 'loopback': 'Loopback', 'ext_recordings': 'Recordings', 'fvs': 'FVS', 'currentDsName': 'DS Name', 'partitionId': 'Partition ID', 'ftpServer': 'FTP Server', 'w2c': 'W2C', 'verint_packages': 'Verint packages', 'domainId': 'Domain ID', 'accountId': 'Account ID', 'sccDomainId': 'SCC Domain ID', 'immediate': 'Immediate', 'domain': 'Domain Name', 'agentCount': 'Agents Count', 'ext_max_conference': 'Max Conference', 'nvoipPdcFarmName': 'NVOIP PDC Farm Name', 'nvoipBdcFarmName': 'NVOIP BDC Farm Name', 'nvoipFarmName': 'Current NVOIP Farm', 'primaryHostNas': 'PDC NAS', 'backupHostNas': 'BDC NAS', 'partitionCodec': 'Domain Codec', 'currentDbHost': 'Current Leader DB', 'currentDbSlaveHost': 'Current Follower DB'},
        'fvs_provisioning': {'grEnabled': 'GR Enabled', 'currentHost': 'Current Host', 'pdcNvoipFarmId': 'PDC NVOIP Farm ID', 'domainName': 'Domain Name', 'currentDc': 'Curent DC', 'bdcNvoipFarmName': 'BDC NVOIP Farm Name', 'bdcNvoipFarmId': 'BDC NVOIP Farm ID', 'domainId': 'Domain ID', 'pdcNvoipFarmName': 'PDC NVOIP Farm Name'},
    }

    def __init__(self, cmd: str, cmd_args: dict):
        super().__init__()
        self.cmd = cmd
        self.cmd_args = cmd_args
        self.CMD_FUNC_MAP: Dict[str, Callable[[Union[List, Dict]], List]] = {
            'jmx_domains': self._beautify_jmx_domains,
            'jmx_calls': self._beautify_jmx_calls,
            'jmx_sessions': self._beautify_jmx_sessions,
            'core': self._beautify_core,
            'db': self._beautify_db_usage,
            'domain_verbose': self._beautify_domain_verbose,
            'domain_numbers': self._beautify_domain_numbers,
            'cnam': self._beautify_cnam,
            'mgrstate': self._beautify_mgrstate,
            'domain': self._beautify_domain_related,
            'account': self._beautify_domain_related,
            'summary': self._beautify_summary,
        }

    # TODO: this method will be abstract, content should be any type probably...
    def format(self, content: Any) -> str:
        """
        Makes the message format reader-friendly based on the command type
        Returns: formatted text
        """
        func = self.CMD_FUNC_MAP.get(self.cmd, self._beautify_other)
        try:
            result = func(content)
        except Exception:
            self._log.critical(f'IMT result parse error:\n{traceback.format_exc()}')
            raise

        return '\n'.join(result)

    def _beautify_jmx_domains(self, content: list):
        return [f'*{partitions_set["domain"]}* ({partitions_set["domainId"]})' for partitions_set in content]

    def _beautify_core(self, content: list):
        partitions = sorted(content, key=lambda k: k['domain'])
        return [f'*{partition["domain"]}* ({partition["domainId"]})' for partition in partitions]

    def _beautify_db_usage(self, content: dict):
        domains = content['domains']
        requested_db_server = content['requested_db_server']
        db_gr_details = '; '.join(f"{k} - {v}" for k, v in content['db_gr_details'].items())
        db_host = requested_db_server['dbHost']

        def dc(host: str):
            return host.split('.')[1]

        rw_domains = []
        rw_domains_ids = []
        ro_domains = []
        ro_domains_ids = []

        for domain in sorted(domains, key=lambda x: x['domain']):
            if dc(domain['currentHost']) == dc(db_host):
                if domain['dbHostCurrent'] in db_host:
                    rw_domains.append(f'{domain["domain"]} ({domain["domainId"]})')
                    rw_domains_ids.append(domain["domainId"])

                if domain['slaveDbHostCurrent'] in db_host:
                    ro_domains.append(f'{domain["domain"]} ({domain["domainId"]})')
                    ro_domains_ids.append(domain["domainId"])

        result = (
            f'*DB Host*: {db_host}',
            f'*DB Role*: {requested_db_server["dbRole"]}',
            f'*DS Name*: {requested_db_server["dbDs"]}',
            f'*DB GR Details*: {db_gr_details}\n'
            '\n',
            '*Read/Write domains list:*',
            '\n'.join(rw_domains),
            '\n',
            '*Read/Write domains ids list:*',
            ';'.join(rw_domains_ids),
            '\n',
            '*Read only domains:*',
            '\n'.join(ro_domains),
            '\n',
            '*Read only domains ids list:*',
            ';'.join(ro_domains_ids)
        )
        return result

    def _beautify_domain_verbose(self, content: list):
        fields_rename_dict = self.RESULT_DICTIONARY_NAMES[self.cmd]
        db_info = []
        result = []
        for domain in content:
            result.append(f'*Domain name:* {domain["domain"]}\n\n')
            for key in domain:
                if domain[key] and key in fields_rename_dict:
                    if key in ('currentDbHost', 'currentDbSlaveHost'):
                        db = f'*{fields_rename_dict[key]}*:   {domain[key]}'
                        if domain['currentReportDb'] == domain[key]:
                            db += ' (Reporting DS)'
                        db_info.append(db)

                    else:
                        domain_info_field = f'*{fields_rename_dict[key]}*:   {domain[key]}'
                        if key == 'bkupHost' and domain[key] != 'Non GR':
                            domain_info_field += ' (permanent)' if domain['bdcPermanent'] == 'Yes' else ' (not permanent)'
                        result.append(domain_info_field)

            # https://five9inc.atlassian.net/browse/PE-896
            gr_host = domain['bkupHost'] if domain['currentHost'] == domain['domainHost'] else domain['domainHost']
            gr_db_leader = domain['bkpDbHost'] if domain['currentDbHost'] == domain['dbHost'] else domain['dbHost']
            gr_db_follower = (domain['bkpDbSlaveHost'] if domain['currentDbSlaveHost'] == domain['dbSlaveHost']
                              else domain['dbSlaveHost'])

            result.append(f'*GR Host*:   {gr_host}')
            result.append(f'*GR DB Leader*:   {gr_db_leader}')
            result.append(f'*GR DB Follower*:   {gr_db_follower}')

        result.extend(db_info)
        return result

    def _beautify_domain_numbers(self, content: list):
        if len(content) > self.MAX_DOMAIN_NUMBERS:  # provisioning asked to limit the output with 200 elements
            content = content[:self.MAX_DOMAIN_NUMBERS + 1]

        result = []
        for number in content:
            campaign = f' ({number.get("cmpName", "")})' if self.cmd_args['campaigns'] else ''
            result.append(f'{number["phoneNum"]}{campaign}')

        return result

    def _beautify_cnam(self, content: list):
        result = [f"```{'Phone number':<15s}    {'Twilio Caller Name':<30s}    {'OpenCNAM Caller Name':30s}```"]
        for n in content:
            tw_caller_name = n.get('tw_caller_name', '')
            op_caller_name = n.get('op_caller_name', '')
            result.append(f'```{n["number"]:<15s}    {tw_caller_name:<30s}    {op_caller_name:30s}```')

        return result

    def _beautify_mgrstate(self, content: list):
        domain_data = content[0]
        domain_state = content[1]

        cur_state = domain_state['migration']['status']['state']
        cur_host = domain_data['currentHost']

        result = [f'*Current Active Domain Host:* {cur_host}',
                  f'*Current MGR Status:* {cur_state}']

        if cur_state not in ('IDLE', 'null'):
            prim = domain_data['domainHost']
            bkp = domain_data['bkupHost']

            from_host, to_host = (prim, bkp) if cur_host == prim else (bkp, prim)
            result.append(f'*Move:* from {from_host} to {to_host}')

            if 'forceTime' in cur_state:
                time_value = cur_state['forceTime']
                eval_time = datetime.utcfromtimestamp(time_value // 1000).strftime('%Y-%m-%d %H:%M:%S')
                result.append(f'*Completion Evaluation (UTC time)*: {eval_time}')

            if "startTime" in cur_state:
                time_value = cur_state['startTime']
                start_time = datetime.utcfromtimestamp(time_value // 1000).strftime('%Y-%m-%d %H:%M:%S')
                result.append(f'*Start (UTC time)*: {start_time}')

        return result

    def _beautify_jmx_calls(self, content: list):
        return content

    def _beautify_jmx_sessions(self, content: list):
        return [f'```{i}```' if 'sessionId' in i else i for i in content]

    def _beautify_domain_related(self, content: list):
        result = []
        for domain in content:
            sat = 'satp2.scl.five9.com'  # TODO: need select func of actual SAT for certain DC
            d_id = domain['domainId']
            d_name = domain['domain']
            d_name_dash = d_name.replace(' ', '_')
            domain_hl = f'<https://{sat}/sat/domain/_search.jsf?Id={d_id}|{d_id}>'
            account_hl = f'<https://{sat}/sat/partition/_partition.jsf?Id={domain["partitionId"]}|{domain["accountId"]}>'
            provider_name = domain['provider_name']

            def jmx_url(host_name: str):
                return (f'<https://{host_name}:8443/jmx-console/HtmlAdaptor?'
                        f'action=inspectMBean&name=five9.app%3AdomainId%3D{d_id}'
                        f'%2CdomainName%3D{d_name_dash}%2Cservice%3Dcom.five9.cc.spi.CallCenterService'
                        f'|{host_name}>')

            cur_host_hl = jmx_url(domain['currentHost'])
            primary_host_hl = jmx_url(domain['domainHost'])
            backup_host_hl = jmx_url(domain['bkupHost'])

            if domain['bkupHost'] == 'Non GR':
                bdc_permanent = ''
            else:
                bdc_permanent = ' (permanent)' if domain['bdcPermanent'] == 'Yes' else ' (not permanent)'

            result.append(f'*Domain:* {d_name} ({domain_hl})')
            result.append(f'*Account:* {domain["accountName"]} ({account_hl})')
            result.append(f'*Primary Host:* {primary_host_hl}')
            result.append(f'*Backup Host:* {backup_host_hl}{bdc_permanent}')
            result.append(f'*Current Host:* {cur_host_hl}')
            result.append(f'*Provider Name:* {provider_name}')

            db_url_no_domain = '.'.join(domain['currentDbHost'].split('.')[:-2])
            result.append(f'*Current DB:* {db_url_no_domain} ({domain["dbName"]})')
            result.append(f'*Current Freedom Farm:* {domain["farmName"] or "None"}')

            if domain['fvs'] == "FGV":
                result.append(f'*Current FVS Farm:* {domain["nvoipFarmName"]} (FGV enabled)')
            elif domain['fvs'] == 'FVS':
                result.append(f'*Current FVS Farm:* {domain["nvoipFarmName"]}')
            else:
                result.append('*FVS:* No')

            result.append('')

        return result

    def _beautify_summary(self, content: Dict):
        result = self._beautify_domain_related(content['domain'])
        jmx_sessions = self._beautify_jmx_sessions(content['jmx_sessions'])
        jmx_calls = self._beautify_jmx_calls(content['jmx_calls'])

        total_sessions = '0'
        sessions_result = ''
        for info_row in jmx_sessions:
            if ':' in info_row and 'Current Host' not in info_row:
                if 'total' in info_row.lower():
                    total_sessions = info_row.split(':')[1]
                else:
                    if 'sessionId' not in info_row:
                        sessions_result += f'{info_row}\n'

        total_calls = '0'
        calls_result = ''
        for info_row in jmx_calls:
            if ('=' in info_row or ':' in info_row) and "Content-Type" not in info_row and 'Host' not in info_row:
                if 'Total calls' in info_row:
                    total_calls = info_row.split("=")[1]
                else:
                    calls_result += info_row.replace('=', ':') + '\n'

        result.append('\n')
        result.append(f'*Total sessions: {total_sessions}*')
        result.append(sessions_result)
        result.append(f'*Total calls: {total_calls}*')
        result.append(calls_result)
        return result

    def _beautify_other(self, content: dict):
        if isinstance(content, dict):
            fields_rename_dict = self.RESULT_DICTIONARY_NAMES.get(self.cmd)
            if fields_rename_dict:
                return [f'*{fields_rename_dict[k]}*:   {v}' for k, v in content.items() if v and k in fields_rename_dict]
            else:
                return [f'*{k}*:   {v}' for k, v in content.items()]

        if isinstance(content, Sequence):
            result = []
            for i in content:
                result += self._beautify_other(i)
                result.append('')
            return result

        else:
            return [str(content)]
