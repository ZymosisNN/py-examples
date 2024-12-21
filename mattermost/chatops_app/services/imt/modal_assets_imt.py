COMMANDS = (
    {'name': 'domain', 'title': 'Domain Basic Info'},
    {'name': 'domain_verbose', 'title': 'Domain Verbose Info'},
    {'name': 'account', 'title': 'Account Info'},
    {'name': 'summary', 'title': 'Summary Domain Info'},
    {'name': 'fvs_provisioning', 'title': 'FVS Provisioning'},
    {'name': 'domain_numbers', 'title': 'Domain Numbers'},
    {'name': 'jmx_domains', 'title': 'JMX Domains'},
    {'name': 'jmx_sessions', 'title': 'JMX Sessions'},
    {'name': 'jmx_calls', 'title': 'JMX Calls', },
    {'name': 'db', 'title': 'DB Server Dependency (DB usage)'},
    {'name': 'core', 'title': 'Core domains'},
    {'name': 'cnam', 'title': 'CNAM'},
    {'name': 'mgrstate', 'title': 'Domain MGR state'},
)

__name_or_id = ({'name': 'name_or_id', 'title': 'Domain name or id', 'input_type': 'entry'},)
__domain_id = ({'name': 'name_or_id', 'title': 'Domain id', 'input_type': 'entry'},)
__core_host = ({'name': 'core_host', 'title': 'Core host', 'input_type': 'entry'},)
CMD_ARGS_MAP = {
    'domain': __name_or_id,
    'domain_verbose': __name_or_id,
    'account': ({'name': 'name_or_id', 'title': 'Account name or id', 'input_type': 'entry'},),
    'fvs_provisioning': __name_or_id,
    'summary': __domain_id,
    'domain_numbers': ({'name': 'name_or_id', 'title': 'Domain id', 'input_type': 'entry'},
                       {'name': 'campaigns', 'title': 'Show campaigns', 'input_type': 'checkbox', 'text_key': '-campaigns'}),
    'jmx_calls': __domain_id,
    'jmx_sessions': __domain_id,
    'jmx_domains': __core_host,
    'core': __core_host,
    'db': ({'name': 'db_host', 'title': 'DB host', 'input_type': 'entry'},),
    'cnam': ({'name': 'phone_numbers', 'title': 'Phone numbers', 'input_type': 'entry'},
             {'name': 'token', 'title': 'Token', 'input_type': 'entry', 'text_key': '-token'}),
    'mgrstate': __domain_id,
}
