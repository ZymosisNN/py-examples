from chatops_app.services.command_arg_parser import CommandArgParser

SRV = '/imt'
CMD_PARSERS = {}

_ = CommandArgParser(prog='help', usage=f'{SRV} [help]', description='Show this help info')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='domain',
                     usage=f'{SRV} domain <domainName|domainId>',
                     description='Returns basic information of the domain with id or domains matching name')
_.add_argument('name_or_id')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='domain_verbose',
                     usage=f'{SRV} domain_verbose <domainName|domainId>',
                     description='Returns detailed information of the domain with id or domains matching name')
_.add_argument('name_or_id')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='account',
                     usage=f'{SRV} account <accountName|accountId>',
                     description='Returns basic information of the account with id or accounts matching name')
_.add_argument('name_or_id')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='summary',
                     usage=f'{SRV} summary <domainId>',
                     description='Returns basic information of the domain with id plus checks JMX for a list '
                                 'of sessions and calls for the given domain on its active core')
_.add_argument('domain_id', type=int)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='fvs_provisioning',
                     usage=f'{SRV} fvs_provisioning <domainName|domainId>',
                     description='Returns basic information on FVS domain configuration')
_.add_argument('name_or_id')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='domain_numbers',
                     usage=f'{SRV} domain_numbers <domainId> [-campaigns]',
                     description="Returns the list of the domain's phone numbers (limited by 200 items). "
                                 "If the key *-campaigns* is added to the request, the output includes campaign name "
                                 "for each number if it's assigned to any")
_.add_argument('domain_id', type=int)
_.add_argument('-campaigns', action='store_true')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='jmx_calls',
                     usage=f'{SRV} jmx_calls <domainId>',
                     description='Checks JMX for a list of calls for the given domain on its cores')
_.add_argument('domain_id', type=int)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='jmx_sessions',
                     usage=f'{SRV} jmx_sessions <domainId>',
                     description='Checks JMX for a list of active user sessions for the given domain on its cores')
_.add_argument('domain_id', type=int)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='jmx_domains',
                     usage=f'{SRV} jmx_domains <coreHost>',
                     description='Checks JMX for a list of domains currently running on the given core')
_.add_argument('core_host')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='db',
                     usage=f'{SRV} db <dbHost>',
                     description='Returns a list of all domains that use defined DB host')
_.add_argument('db_host')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='core',
                     usage=f'{SRV} core <coreHost>',
                     description='Returns a list of all domains currently using defined core host')
_.add_argument('core_host')
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='cnam',
                     usage=f'{SRV} cnam <phoneNumber> [phoneNumber ...] -token <authorizationToken>',
                     description='_Available only in US DC_\n'
                                 "Returns the indicated number's CNAM for two providers: OpenCNAM and Twilio. "
                                 'You may also indicate several phone numbers, separated by space: '
                                 '*/imt cnam <number1> <number2> <number3> -token <authorizationToken>*')
_.add_argument('phone_numbers', nargs='+')
_.add_argument('-token', required=True)
CMD_PARSERS[_.prog] = _

_ = CommandArgParser(prog='mgrstate',
                     usage=f'{SRV} mgrstate <domainId>',
                     description='_Currently is available only in US DC_\nReturns the MGR status of a given domain.')
_.add_argument('domain_id', type=int)
CMD_PARSERS[_.prog] = _
