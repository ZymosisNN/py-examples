import logging
from typing import Dict, List, Tuple, Optional

from django.core import exceptions
from django.utils.timezone import now

from chatops_app.abstracts import ChatOpsError
from . import models


class StorageError(ChatOpsError):
    pass


class ObjectAlreadyExists(StorageError):
    pass


class ObjectDoesNotExist(StorageError):
    pass


_sat_url_per_provider = {
    'US': {
        138: 'https://satp1.scl.five9.com/sat-api/v1',
        148: 'https://satp2.scl.five9.com/sat-api/v1',
        3000000000000000011: 'https://satp1.atl.five9.com/sat-api/v1',
        3000000000000000021: 'https://satp2.atl.five9.com/sat-api/v1',
    },
    'EU': {
        400000000000000001: 'https://satp1.ldn.five9.com/sat-api/v1',
        400000000000011: 'https://satp2.ldn.five9.com/sat-api/v1',
        500000000000011: 'https://satp1.ldn1.five9.com/sat-api/v1',
        500000000000012: 'https://satp2.ldn1.five9.com/sat-api/v1',
        4000000000000000001: 'https://satp1.ams.five9.com/sat-api/v1',
        500000000000001: 'https://satp2.ams.five9.com/sat-api/v1',
    },
    'QA01': {
        1: 'https://qaus01.five9lab.com/sat-api/v1',
        2: 'https://qaus03.five9lab.com/sat-api/v1',
    },
    'TAG03': {  # TODO: workaround unless LAB-2496 is done
        1: 'https://qasat621.scl.five9lab.com:8443/sat-api/v1',
        21: 'https://qasat621.scl.five9lab.com:8443/sat-api/v1',
        11: 'https://qasat621.scl.five9lab.com:8443/sat-api/v1',
        31: 'https://qasat621.scl.five9lab.com:8443/sat-api/v1',
        # 1: 'https://qasat61.five9lab.com/sat-api/v1',
        # 21: 'https://qasat62.five9lab.com/sat-api/v1',
        # 11: 'https://qasat63.five9lab.com/sat-api/v1',
        # 31: 'https://qasat64.five9lab.com/sat-api/v1',
    },
    'TAG04': {
        1: 'https://tagsat01.five9lab.com/sat-api/v1',
        21: 'https://tagsat02.five9lab.com/sat-api/v1',
        11: 'https://tagsat03.five9lab.com/sat-api/v1',
        31: 'https://tagsat04.five9lab.com/sat-api/v1',
    },
}

_log = logging.getLogger(__name__.split('.')[-1])


def get_user_data(user_id: str) -> Dict:
    user = models.SlackUser.objects.get(slack_user_id=user_id)
    res = {
        'usergroups': user.groups_list.split(' ') if user.groups_list else [],
        'allowed_commands': user.allowed_commands.split(' ') if user.allowed_commands else []
    }
    _log.debug(f'User({user_id}): {res}')
    return res


def get_cmd_permissions(cmd_name: str):
    cmd = models.ServicePermissions.objects.get(service=cmd_name)
    allowed_groups = cmd.allowed_groups.split(' ') if cmd.allowed_groups else []
    _log.debug(f'Command "{cmd_name}" allowed_groups: {allowed_groups}')
    return allowed_groups


def get_sat_url(provider_id: int, dc: str):
    dc = dc.upper()
    try:
        providers = _sat_url_per_provider[dc.upper()]
    except KeyError:
        raise RuntimeError(f'Unknown DC "{dc}", allowed: {list(_sat_url_per_provider.keys())}')
    try:
        return providers[provider_id]
    except KeyError:
        raise RuntimeError(f'Unknown provider id={provider_id}, allowed: {list(_sat_url_per_provider[dc].keys())}')


def add_mgr_queue(name: str, direction: str, timer: str, slack_user_id: str):
    open_state = models.MgrQueueState.objects.get(name='Open')
    try:
        models.MgrQueue.objects.get(name=name, state=open_state)
        raise ObjectAlreadyExists(f'Open queue with name "{name}" already exists')
    except exceptions.ObjectDoesNotExist:
        pass
    user = models.SlackUser.objects.get(slack_user_id=slack_user_id)
    queue = models.MgrQueue(name=name, direction=direction, timer=timer, opened_by=user, state=open_state)
    queue.save()
    _log.info(f'Added {queue}')


def close_mgr_queue(name: str, slack_user_id: str) -> None:
    queue = _get_open_queue(name)
    added_domain_state = models.MgrDomainState.objects.get(name='Requested')
    if models.MgrDomain.objects.filter(queue=queue, state=added_domain_state):
        raise ObjectAlreadyExists(f'Queue "{name}" has not processed domains')

    closed_state = models.MgrQueueState.objects.get(name='Closed')
    user = models.SlackUser.objects.get(slack_user_id=slack_user_id)
    queue.state = closed_state
    queue.closed_by = user
    queue.time_closed = now()
    queue.save()
    _log.info(f'Closed {queue}')


def get_mgr_queues(closed=False) -> List[Dict]:
    state_str = 'Closed' if closed else 'Open'
    state = models.MgrQueueState.objects.get(name=state_str)
    queues = models.MgrQueue.objects.filter(state=state)
    _log.info(f'{state_str} queues: {queues}')
    return [queue.to_dict() for queue in queues]


def get_mgr_queue_status(name: str) -> Tuple[Dict, List[Dict]]:
    queue = _get_open_queue(name)
    domains = models.MgrDomain.objects.filter(queue=queue)
    if not domains:
        raise ObjectDoesNotExist(f'Queue "{name}" has no domains')

    _log.info(f'Queue: {queue}')
    _log.info(f'Domains: {domains}')
    return queue.to_dict(), [domain.to_dict() for domain in domains]


def add_mgr_domain(qname: str, domain_id: int, domain_name: str, slack_user_id: str) -> None:
    queue = _get_open_queue(qname)
    try:
        models.MgrDomain.objects.get(domain_id=domain_id, queue=queue)
        raise ObjectAlreadyExists(f'Domain with ID={domain_id} already added into queue "{qname}"')
    except exceptions.ObjectDoesNotExist:
        pass
    user = models.SlackUser.objects.get(slack_user_id=slack_user_id)
    state = models.MgrDomainState.objects.get(name='Requested')
    domain = models.MgrDomain(domain_id=domain_id, name=domain_name, queue=queue, requested_by=user, state=state)
    domain.save()
    _log.info(f'Added {domain}')


def pull_domains(qname: str, slack_user_id: str, domain_ids: Optional[List[int]] = None) -> List[int]:
    queue = _get_open_queue(qname)
    requested_state = models.MgrDomainState.objects.get(name='Requested')
    domains = models.MgrDomain.objects.filter(queue=queue, state=requested_state)
    if domain_ids:
        domains = domains.filter(domain_id__in=domain_ids)
    if not domains:
        raise ObjectDoesNotExist(f'No unprocessed domains from requested in queue "{qname}"')

    update_domains_ids = [domain.domain_id for domain in domains]
    processed_state = models.MgrDomainState.objects.get(name='Processed')
    user = models.SlackUser.objects.get(slack_user_id=slack_user_id)
    domains.update(state=processed_state, processed_by=user)
    _log.info(f'Processed {update_domains_ids}')
    return update_domains_ids


def _get_open_queue(name: str):
    open_state = models.MgrQueueState.objects.get(name='Open')
    try:
        return models.MgrQueue.objects.get(name=name, state=open_state)
    except exceptions.ObjectDoesNotExist:
        raise ObjectDoesNotExist(f'Queue with name "{name}" is either not found or closed')
