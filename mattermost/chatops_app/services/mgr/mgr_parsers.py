from chatops_app.services.command_arg_parser import CommandArgParser

SRV = '/mgr'
CMD_PARSERS = {}

_ = CommandArgParser(prog='help', usage=f'{SRV} [help]', description='Shows this help info')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='request', usage=f'{SRV} request', description='Opens modal for adding domains into queue')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_add',
                     usage=f'{SRV} queue_add -n|--name <queueName> -d|--dir <DC direction> -t|--timer <timeframe>',
                     description='Creates the queue with the indicated name and direction in the DB.\nPlease note that '
                                 'queue names are not case sensitive.')
_.add_argument('-n', '--name', dest='queue_name', required=True)
_.add_argument('-d', '--dir', dest='direction', required=True)
_.add_argument('-t', '--timer', dest='timer', required=True)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_list',
                     usage=f'{SRV} queue_list (optional: -c|--closed)',
                     description='Lists all active queues. The command with `-c|--closed` key lists all closed queues')
_.add_argument('-c', '--closed', dest='closed', action='store_true', required=False)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_close',
                     usage=f'{SRV} queue_close <queueName>',
                     description='Closes the indicated queue')
_.add_argument('queue_name')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_status',
                     usage=f'{SRV} queue_status <queueName>',
                     description='Shows status of all domains (if added) for the indicated queue')
_.add_argument('queue_name')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_pull',
                     usage=f'{SRV} queue_pull -n|--name <queueName> -d|--domains <domainID1 domainID2 ...>',
                     description='Pulls domains with defined IDs from the queue')
_.add_argument('-n', '--name', dest='queue_name', required=True)
_.add_argument('-d', '--domains', dest='domain_ids', type=int, nargs='+', required=True)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_pull_all',
                     usage=f'{SRV} queue_pull_all <queueName>',
                     description='Pulls all domains from the queue')
_.add_argument('queue_name')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='queue_domain_add',
                     usage=f'{SRV} queue_domains_add -q <queueName> -d <domainID>',
                     description='Add domain with defined ID into the queue with defined name',
                     internal=True)
_.add_argument('-q', dest='queue_name', required=True)
_.add_argument('-d', dest='domain_id', type=int, required=True)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='get_queues', internal=True)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='get_queue_info', internal=True)
_.add_argument('queue_name')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='get_domain_info', internal=True)
_.add_argument('domain_id', type=int)
CMD_PARSERS[_.prog] = _
