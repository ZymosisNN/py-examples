import collections
import logging
import re
import shlex
from typing import Dict

from chatops_app.abstracts import ChatOpsError
from chatops_app.services.command_arg_parser import CommandArgParser, CommandArgParserError

CMD_ALIASES = {
    'interactive': 'int',
    'fvs_prov': 'fvs_provisioning',
}


class CmdStrParserError(ChatOpsError):
    pass


class CmdStrParser:
    _parsers: Dict[str, Dict[str, CommandArgParser]] = {}

    def __init__(self, srv_name: str, raw_cmd_str: str):
        self._log = logging.getLogger(f'{self.__class__.__name__}({srv_name})')
        self.srv_name = srv_name
        self._log.debug(f'Raw cmd string: "{raw_cmd_str}"')

        raw_cmd_str = self._purify_cmd_str(raw_cmd_str)
        self._log.debug(f'Purified cmd string: "{raw_cmd_str}"')

        self._cmd, *args = shlex.split(raw_cmd_str)
        self._log.debug(f'Raw arg list: {args}')

        try:
            srv_parsers = self._parsers[srv_name]
        except KeyError:
            self._log.error(f'Parsers for "{srv_name}" is not registered')
            raise CmdStrParserError(f'Unknown slash command: `/{srv_name}`')

        try:
            parser = srv_parsers[self._cmd]
        except KeyError:
            self._log.error(f'Parser for command: "{self._cmd}" is not found')
            raise CmdStrParserError(f'Unknown command: `{self._cmd}`\nSend `/{srv_name}` to see list of commands')

        try:
            self._args = vars(parser.parse_args(args))
        except CommandArgParserError as ex:
            self._log.error(ex)
            raise CmdStrParserError(f'{ex}\n{parser.format_usage()}') from ex

        self._log.debug(f'Command: {self.cmd}')
        self._log.debug(f'   Args: {self.args}')

    @classmethod
    def register_parsers(cls, srv_name: str, srv_parsers: Dict[str, CommandArgParser]):
        if srv_name in cls._parsers:
            raise CmdStrParserError(f'Parsers for "{srv_name}" have already been registered')
        cls._parsers[srv_name] = srv_parsers

    @property
    def cmd(self):
        return self._cmd

    @property
    def args(self):
        return self._args

    @property
    def usage(self):
        return [{'command': p.prog, 'usage': p.usage, 'description': p.description}
                for p in self._parsers[self.srv_name].values() if not p.internal]

    # TODO: perhaps it's needed to be improved
    def _purify_cmd_str(self, cmd_str: str):
        """ Fool protection: remove rubbish, join space separated commands """
        self._log.debug(f'----> purify_cmd_str: "{cmd_str}"')
        cmd_str = cmd_str.strip()

        # For some rare but still couple times appeared cases
        cmd_str = cmd_str.replace('\xc2\xa0', ' ').replace('\xa0', ' ')

        # Remove slack parsed italic (_param_) parameters
        c_italic = collections.Counter(cmd_str)['_']
        if c_italic == 2:
            if ' _' in cmd_str:  # only when special symbol surrounds the word-phrase
                cmd_str = cmd_str.replace('_', '')

        # Remove slack parsed bold (*_param_*) parameters
        c_bold = collections.Counter(cmd_str)['*']
        if c_bold == 2:
            cmd_str = cmd_str.replace('*', '')
        self._log.debug(f'    de-markdown: {cmd_str}')

        # Apply aliases
        for cmd_from, cmd_to in CMD_ALIASES.items():
            cmd_str = re.sub(rf'^{cmd_from}\b', cmd_to, cmd_str)
        self._log.debug(f'    aliasing: {cmd_str}')

        # Applying quotes to a string where they should be initially. God forgive me...
        impacted_cmds = 'domain|domain_verbose|account|fvs_provisioning'
        params = ' -all.*| -thread.*| -dc .*'
        cmd_str = re.sub(rf'^({impacted_cmds}) (.+?)({params})?$', r'\1 "\2"\3', cmd_str)
        self._log.debug(f'    add quotes: {cmd_str}')

        self._log.debug('<----')
        return cmd_str
