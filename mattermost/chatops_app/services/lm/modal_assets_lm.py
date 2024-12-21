from typing import NamedTuple


class NodeIds(NamedTuple):
    DASHBOARD_GROUP = 'dashboard_group'
    DASHBOARD = 'dashboard'
    WIDGET = 'widget'
    TIMEFRAME = 'timeframe'


INIT_CMD = 'get_dashboard_groups'


ACTION_TO_COMMAND_MAP = {
    NodeIds.DASHBOARD_GROUP: 'get_dashboards',
    NodeIds.DASHBOARD: 'get_widgets'
}
