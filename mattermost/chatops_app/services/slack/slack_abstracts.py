import re
from abc import ABC, abstractmethod
from typing import Dict

from chatops_app.abstracts import NameAndLogMixin
from .slack_payloads import SlackModalPayload


class AbstractModalLogic(ABC, NameAndLogMixin):
    def is_modal_opener(self, cmd: str) -> bool:
        return bool(re.match(r'int(eractive)?\b', cmd))

    def get_init_cmd(self) -> str:
        return ''

    def get_cmd_for_action(self, payload: SlackModalPayload) -> str:
        return ''

    @abstractmethod
    def get_cmd_for_submit(self, payload: SlackModalPayload) -> str: ...
    @abstractmethod
    def build_modal_view(self, data: Dict) -> Dict: ...
