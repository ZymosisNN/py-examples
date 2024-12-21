from datetime import datetime
from typing import Dict, List, Tuple, Union

import prettytable

from chatops_app.services.slack import slack_markdown as md

TIMESTAMP_FMT = '%d %b %Y %H:%M'
TOO_MANY_DOMAINS_THRESHOLD = 20


def format_queue_list(queues: List[Dict]) -> md:
    keys_rename = {
        'name': 'Name',
        # 'state': 'State',
        'direction': 'Dir',
        'timer': 'Timer',
        'opened_by': 'Opened by',
        'time_opened': 'Open time',
    }
    state = queues[0]["state"]
    if state == 'Closed':
        keys_rename.update({
            'closed_by': 'Closed by',
            'time_closed': 'Closed time',
        })
    msg = md.ok(f'{state} MGR queues:').br()
    _format_dict(queues, keys_rename)
    table = prettytable.PrettyTable(field_names=queues[0].keys())
    table.add_rows(i.values() for i in queues)
    msg.code(table)
    return msg


def format_queue_status(queue: Dict, domains: List[Dict]) -> Union[Tuple[md.MD, str], md.MD]:
    keys_rename = {
        'domain_id': 'Domain ID',
        'name': 'Name',
        'state': 'State',
        'requested_by': 'Requested by',
        'processed_by': 'Processed by',
        'mgr_state': 'MGR State',
    }

    state = queue['state']
    msg = (
        md.ok(f'MGR queue ').b(queue['name'])(':').br()
        ('State: ').b(state).br()
        ('Direction: ').b(queue['direction']).br()
        ('Timer: ').b(queue['timer']).br()
        ('Opened by: ').b(queue['opened_by']).br()
        ('Open time: ').b(queue['time_opened'].strftime(TIMESTAMP_FMT))
    )
    if state == 'Closed':
        time_closed = queue['time_closed'].strftime(TIMESTAMP_FMT)
        msg.br().b('Closed by: ')(queue['closed_by']).br().b('Closed time: ')(time_closed).br()

    _format_dict(domains, keys_rename)

    table = prettytable.PrettyTable(field_names=domains[0].keys())
    table.add_rows(i.values() for i in domains)

    if len(domains) > TOO_MANY_DOMAINS_THRESHOLD:
        return msg, str(table)

    msg.code(table)
    return msg


def _format_dict(data: List[Dict], keys_rename: Dict[str, str]) -> None:
    for item in data:
        for key in list(item):
            value = item.pop(key)
            if key in keys_rename:
                value = value.strftime(TIMESTAMP_FMT) if isinstance(value, datetime) else value
                item[keys_rename[key]] = value or ''


if __name__ == '__main__':
    test_queues = [
        dict(name=f'queue-name-{i}', state='Closed', direction='SCL', opened_by='kgordeev',
             time_opened=datetime.now(), closed_by='medved', time_closed=datetime.now(), timer='10m')
        for i in range(3)
    ]
    print(format_queue_list(test_queues), '\n')

    q = dict(name=f'queue-name', state='Closed', direction='SCL', opened_by='kgordeev',
             time_opened=datetime.now(), closed_by='medved', time_closed=datetime.now(), timer='10m')
    d = [
        dict(domain_id=110 + i, name=f'domain-{i}', state='Added', requested_by='kgordeev', processed_by=None)
        for i in range(3)
    ]

    print(format_queue_status(q, d))
