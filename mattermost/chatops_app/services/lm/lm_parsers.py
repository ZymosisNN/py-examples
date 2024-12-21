from chatops_app.services.command_arg_parser import CommandArgParser

SRV = '/lmw'
CMD_PARSERS = {}

_ = CommandArgParser(prog='help', usage=f'{SRV} [help]', description='Show this help info')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='show',
                     usage=f'{SRV} show (-wid <widgetId> | (-w <widgetName> -d <dashboardName>)) -t <timeframe>',
                     description='Returns the widget with indicated id or matching the names pair '
                                 '<widgetName> and <dashboardName> for the requested timeframe. Timeframe is '
                                 'requested in the format "30m", "1h" etc. Example: `/lmw show -d AMS ENV Servers '
                                 '-w JVM Memory -t 30m` (where "AMS ENV Servers" is the dashboard name, and '
                                 '"JVM Memory" is the widget name). Pay attention that dashboard/widget names are '
                                 'to be indicated without quotes.')
_widget = _.add_mutually_exclusive_group(required=True)
_widget.add_argument('-wid', dest='widget_id')
_widget.add_argument('-w', dest='widget_name_parts', nargs='+')
_.add_argument('-d', dest='dashboard_name_parts', nargs='+')
_.add_argument('-t', dest='timeframe', required=True)
_.add_argument('-e', dest='environment', default='production')
CMD_PARSERS[_.prog] = _

"""
Internal command parsers
"""
_ = CommandArgParser(prog='get_dashboard_groups', internal=True)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='get_dashboards', internal=True)
_.add_argument('dashboard_group')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='get_widgets', internal=True)
_.add_argument('dashboard')
CMD_PARSERS[_.prog] = _
