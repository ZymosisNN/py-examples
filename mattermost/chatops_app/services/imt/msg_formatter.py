import logging
from datetime import datetime
from typing import Dict, Sequence

import prettytable

from chatops_app.services import msg_format_tools as fmt
from chatops_app.services.slack import slack_markdown as md

MAX_DOMAIN_NUMBERS = 200
RESULT_DICTIONARY_NAMES = {
    'account': {'farmName': 'Freedom Farm', 'accountName': 'Account Name', 'dbName': 'DB Name', 'mmHost': 'MM Host', 'ext_nsp_agents': 'NetSuite+  Agents', 'acBoards': 'AC Boards', 'bkupHost': 'Backup Host', 'currentHost': 'Current Host', 'allDay': '24/7', 'ext_adtp_agents': 'ADT+ Agents', 'ext_orp_agents': 'Oracle+ Agents', 'ext_inbound_lines': 'Inbound lines', 'ext_outbound_lines': 'Outbound lines', 'domainHost': 'Primary Host', 'ext_msdp_agents': 'MS Dynamics+ Agents', 'ext_zdp_agents': 'Zendesk+ Agents', 'sipTrunks': 'SIP Trunks', 'dynamicFtp': 'Dynamic FTP', 'loopback': 'Loopback', 'ext_recordings': 'Recordings', 'fvs': 'FVS', 'dsName': 'DS Name', 'partitionId': 'Partition ID', 'ftpServer': 'FTP Server', 'w2c': 'W2C', 'dbHost': 'DB host', 'verint_packages': 'Verint packages', 'domainId': 'Domain ID', 'accountId': 'Account ID', 'sccDomainId': 'SCC Domain ID', 'immediate': 'Immediate', 'domain': 'Domain Name', 'agentCount': 'Agents Count', 'ext_max_conference': 'Max Conference', 'nvoipPdcFarmName': 'NVOIP PDC Farm Name', 'nvoipBdcFarmName': 'NVOIP BDC Farm Name', 'nvoipFarmName': 'Current NVOIP Farm', 'primaryHostNas': 'PDC NAS', 'backupHostNas': 'BDC NAS', 'partitionCodec': 'Domain Codec'},
    'domain': {'accountName': 'Account', 'dbName': 'Current DB', 'currentHost': 'Current Host', 'domain': 'Domain'},
    'domain_verbose': {'farmName': 'Freedom Farm', 'accountName': 'Account Name', 'dbName': 'DB Name', 'mmHost': 'MM Host', 'ext_nsp_agents': 'NetSuite+  Agents', 'acBoards': 'AC Boards', 'bkupHost': 'Backup Host', 'currentHost': 'Current Host', 'allDay': '24/7', 'ext_adtp_agents': 'ADT+ Agents', 'ext_orp_agents': 'Oracle+ Agents', 'ext_inbound_lines': 'Inbound lines', 'ext_outbound_lines': 'Outbound lines', 'domainHost': 'Primary Host', 'ext_msdp_agents': 'MS Dynamics+ Agents', 'ext_zdp_agents': 'Zendesk+ Agents', 'sipTrunks': 'SIP Trunks', 'dynamicFtp': 'Dynamic FTP', 'loopback': 'Loopback', 'ext_recordings': 'Recordings', 'fvs': 'FVS', 'currentDsName': 'DS Name', 'partitionId': 'Partition ID', 'ftpServer': 'FTP Server', 'w2c': 'W2C', 'verint_packages': 'Verint packages', 'domainId': 'Domain ID', 'accountId': 'Account ID', 'sccDomainId': 'SCC Domain ID', 'immediate': 'Immediate', 'domain': 'Domain Name', 'agentCount': 'Agents Count', 'ext_max_conference': 'Max Conference', 'nvoipPdcFarmName': 'NVOIP PDC Farm Name', 'nvoipBdcFarmName': 'NVOIP BDC Farm Name', 'nvoipFarmName': 'Current NVOIP Farm', 'primaryHostNas': 'PDC NAS', 'backupHostNas': 'BDC NAS', 'partitionCodec': 'Domain Codec', 'currentDbHost': 'Current Leader DB', 'currentDbSlaveHost': 'Current Follower DB'},
    'fvs_provisioning': {'grEnabled': 'GR Enabled', 'currentHost': 'Current Host', 'pdcNvoipFarmId': 'PDC NVOIP Farm ID', 'domainName': 'Domain Name', 'currentDc': 'Curent DC', 'bdcNvoipFarmName': 'BDC NVOIP Farm Name', 'bdcNvoipFarmId': 'BDC NVOIP Farm ID', 'domainId': 'Domain ID', 'pdcNvoipFarmName': 'PDC NVOIP Farm Name'},
}


def format_domain_related_list(content: list[dict]) -> md.MD:
    msg = md.MD()
    for domain in content:
        msg += format_domain_related(domain).br()

    return msg


def format_domain_related(domain: dict) -> md.MD:
    msg = md.MD()
    sat = 'satp2.scl.five9.com'  # TODO: need select func of actual SAT for certain DC
    d_id = domain['domainId']
    d_name = domain['domain']
    d_name_dash = d_name.replace(' ', '_')
    domain_link = md.link(f'https://{sat}/sat/domain/_search.jsf?Id={d_id}',
                          d_id)
    account_link = md.link(f'https://{sat}/sat/partition/_partition.jsf?Id={domain["partitionId"]}',
                           domain['accountId'])

    def jmx_url(host_name: str) -> md.MD:
        # TODO: use some URL class
        return md.link(
            url=f'https://{host_name}:8443/jmx-console/HtmlAdaptor?action=inspectMBean&name=five9.app%3AdomainId%3D'
                f'{d_id}%2CdomainName%3D{d_name_dash}%2Cservice%3Dcom.five9.cc.spi.CallCenterService',
            label=host_name
        )

    cur_host_link = jmx_url(domain['currentHost'])
    primary_host_link = jmx_url(domain['domainHost'])
    backup_host_link = jmx_url(domain['bkupHost'])

    if domain['bkupHost'] == 'Non GR':
        bdc_permanent = ''
    else:
        bdc_permanent = '(permanent)' if domain['bdcPermanent'] == 'Yes' else '(not permanent)'

    msg.key_value('Domain', d_name)(' ')(domain_link).br()
    msg.key_value('Account', domain['accountName'])(' ')(account_link).br()
    msg.key_value('Primary Host', primary_host_link).br()
    msg.key_value('Backup Host', backup_host_link)(' ')(bdc_permanent).br()
    msg.key_value('Current Host', cur_host_link).br()

    db_url_no_domain = '.'.join(domain['currentDbHost'].split('.')[:-2])
    msg.key_value('Current DB', db_url_no_domain)(' ')(domain['dbName']).br()
    msg.key_value('Current Freedom Farm', domain['farmName'] or 'None').br()

    if domain['fvs'] == "FGV":
        msg.key_value('Current FVS Farm', domain['nvoipFarmName'])(' (FGV enabled)')
    elif domain['fvs'] == 'FVS':
        msg.key_value('Current FVS Farm', domain['nvoipFarmName'])
    else:
        msg.key_value('FVS', 'No')

    return msg


def format_summary(content: Dict):
    msg = format_domain_related(content['domain']).br()

    total_sessions = 0
    sessions_result = md.MD()

    # TODO: remove logging
    log = logging.getLogger('TEMPORARY')
    for info_row in content['jmx_sessions']:
        log.critical('=' * 50)
        log.critical(f'info_row = {info_row}')

        # TODO: optimize "ifs"
        if 'sessionId' in info_row and ':' in info_row and 'Current Host' not in info_row:
            if 'total' in info_row.lower():
                total_sessions = info_row.split(':')[1]
            elif 'sessionId' not in info_row:
                sessions_result(info_row).br()

    total_calls = 0
    calls_result = md.MD()
    for info_row in content['jmx_calls']:
        if ('=' in info_row or ':' in info_row) and "Content-Type" not in info_row and 'Host' not in info_row:
            if 'Total calls' in info_row:
                total_calls = info_row.split("=")[1]
            else:
                calls_result(info_row.replace('=', ':')).br()

    msg.b(f'Total sessions: {total_sessions}').br()
    msg += sessions_result
    msg.b(f'Total calls: {total_calls}').br()
    msg += calls_result
    return msg


def format_default(cmd: str, content: dict) -> md.MD:
    msg = md.MD()
    if isinstance(content, dict):
        key_rename = RESULT_DICTIONARY_NAMES.get(cmd)
        if key_rename:  # TODO: walrus
            content = fmt.rename_and_format_dict(content, key_rename)
        for key, value in content:
            msg(f'{key}:    ').b(value).br()

    elif isinstance(content, Sequence):
        for i in content:
            msg(format_default(cmd, i)).br()

    else:
        msg(content)

    return msg


def format_jmx_domains(content: list[Dict]) -> md.MD:
    msg = md.MD()
    for partitions_set in content:
        msg.b(partitions_set['domain'])(f' ({partitions_set["domainId"]})')
    return msg
    # return [f'*{partitions_set["domain"]}* ({partitions_set["domainId"]})' for partitions_set in content]


def format_core(content: list[Dict]) -> md.MD:
    msg = md.MD()
    for partition in sorted(content, key=lambda x: x['domain']):
        msg.b(partition['domain'])(f' ({partition["domainId"]})')
    return msg
    # return [f'*{partition["domain"]}* ({partition["domainId"]})' for partition in partitions]


def format_db_usage(content: dict) -> md.MD:
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

    msg = (
        md.MD('DB Host: ').b(db_host).br()
        ('DB Role: ').b(requested_db_server['dbRole']).br()
        ('DS Name: ').b(requested_db_server['dbDs']).br()
        ('DB GR Details: ').b(db_gr_details).br().br().br()
        ('Read/Write domains list:').b('\n'.join(rw_domains)).br().br()
        ('Read/Write domains ids list:').b(';'.join(rw_domains_ids)).br().br()
        ('Read only domains:').b('\n'.join(ro_domains)).br().br()
        ('Read only ids domains:').b(';'.join(ro_domains_ids))
    )
    # result = (
    #     f'*DB Host*: {db_host}',
    #     f'*DB Role*: {requested_db_server["dbRole"]}',
    #     f'*DS Name*: {requested_db_server["dbDs"]}',
    #     f'*DB GR Details*: {db_gr_details}\n'
    #     '\n',
    #     '*Read/Write domains list:*',
    #     '\n'.join(rw_domains),
    #     '\n',
    #     '*Read/Write domains ids list:*',
    #     ';'.join(rw_domains_ids),
    #     '\n',
    #     '*Read only domains:*',
    #     '\n'.join(ro_domains),
    #     '\n',
    #     '*Read only domains ids list:*',
    #     ';'.join(ro_domains_ids)
    # )
    return msg


def format_domain_verbose(cmd: str, content: list[dict]):
    key_rename = RESULT_DICTIONARY_NAMES[cmd]
    msg = md.MD()
    db_msg = md.MD()
    for domain in content:
        msg('Domain name: ').b(domain['domain']).br().br()
        for key, value in domain.items():
            if value and key in key_rename:
                if key in ('currentDbHost', 'currentDbSlaveHost'):
                    db_msg(key_rename[key])(': ').b(value)
                    if domain['currentReportDb'] == value:
                        db_msg(' (Reporting DS)')
                    db_msg.br()
                else:
                    msg(key_rename[key])(': ').b(value)
                    if key == 'bkupHost' and value != 'Non GR':
                        msg(' (permanent)' if domain['bdcPermanent'] == 'Yes' else ' (not permanent)')
                    msg.br()

    return msg + db_msg


def format_domain_numbers(content: list[dict], campaigns: bool) -> md.MD:
    if len(content) > MAX_DOMAIN_NUMBERS:  # provisioning asked to limit the output with 200 elements
        content = content[:MAX_DOMAIN_NUMBERS + 1]

    msg = md.MD()
    for number in content:
        campaign = f' ({number.get("cmpName", "")})' if campaigns else ''
        msg(f'{number["phoneNum"]}{campaign}').br()

    return msg


def format_cnam(content: list[dict]) -> md.MD:
    # result = [f"```{'Phone number':<15s}    {'Twilio Caller Name':<30s}    {'OpenCNAM Caller Name':30s}```"]
    # tw_caller_name = n.get('tw_caller_name', '')
    # op_caller_name = n.get('op_caller_name', '')
    # msg.code(f'{n["number"]:<15s}    {tw_caller_name:<30s}    {op_caller_name:30s}')
    cnam = [
        {'Phone number': n,
         'Twilio Caller Name': n.get('tw_caller_name', ''),
         'OpenCNAM Caller Name': n.get('op_caller_name', '')}
        for n in content
    ]
    table = prettytable.PrettyTable(field_names=cnam[0].keys())
    table.add_rows(i.values() for i in cnam)
    msg = md.MD().code(table)
    return msg


def format_mgrstate(content: list):
    domain_data = content[0]
    domain_state = content[1]

    cur_state = domain_state['migration']['status']['state']
    cur_host = domain_data['currentHost']

    msg = (
        md.MD('Current Active Domain Host: ').b(cur_host).br()
        ('Current MGR Status: ').b(cur_state).br()
    )
    if cur_state not in ('IDLE', 'null'):
        prim = domain_data['domainHost']
        bkp = domain_data['bkupHost']

        from_host, to_host = (prim, bkp) if cur_host == prim else (bkp, prim)
        msg.b('Move: ')(f'from {from_host} to {to_host}').br()

        ts_fmt = '%Y-%m-%d %H:%M:%S'
        if 'forceTime' in cur_state:
            time_value = cur_state['forceTime']
            eval_time = datetime.utcfromtimestamp(time_value // 1000).strftime(ts_fmt)
            msg('Completion Evaluation (UTC time): ').b(eval_time).br()

        if "startTime" in cur_state:
            time_value = cur_state['startTime']
            start_time = datetime.utcfromtimestamp(time_value // 1000).strftime(ts_fmt)
            msg('Start (UTC time): ').b(start_time).br()

    return msg


# TODO: need this?
def _beautify_jmx_calls(content: list) -> md.MD:
    msg = md.MD()
    for i in content:
        msg(i)
    return msg
    # return content


def _beautify_jmx_sessions(content: list) -> md.MD:
    msg = md.MD()
    for i in content:
        if 'sessionId' in i:
            msg.code(i).br()
        else:
            msg(i).br()

    return msg
    # return [f'```{i}```' if 'sessionId' in i else i for i in content]
