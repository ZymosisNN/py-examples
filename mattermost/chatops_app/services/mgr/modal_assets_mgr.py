from typing import NamedTuple


class NodeIds(NamedTuple):
    QUEUE_NAMES = 'queue_names'
    QUEUE_SELECT = 'queue_select'
    QUEUE_INFO = 'queue_info'
    DOMAIN = 'domain'
    DOMAIN_INFO = 'domain_info'


INIT_CMD = 'get_queues'

ACTION_TO_COMMAND_MAP = {
    NodeIds.QUEUE_SELECT: 'get_queue_info',
    NodeIds.DOMAIN_INFO: 'get_domain_info',
}
