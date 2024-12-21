import json
import logging
import sys
from threading import RLock
from typing import Iterable, Any

import allure
import yaml

DEFAULT_DICT_INDENT = 25
DEFAULT_JSON_INDENT = 2

TRACE = 5
logging.addLevelName(TRACE, 'TRACE')


class LogMixin:
    """
    Mixin class for entities which write logs. It contains useful methods for quick and nice logs.
    """
    _lock = RLock()

    def __init__(self, subname: str | None = None) -> None:
        name = f'{self.__class__.__name__}{f"({subname})" if subname else ""}'
        self.log = logging.getLogger(name)

    def trace(self, msg: Any) -> None:
        self.log.log(TRACE, msg)

    def log_list(self, data: Iterable, description: str = '', level: int = logging.DEBUG) -> None:
        with self._lock:
            if description:
                self.log.log(level, description)

            for i in data:
                self.log.log(level, f'    {i}')
            self.log.log(level, '')

    def log_dict(self, data: dict,
                 description: str = '',
                 level: int = logging.DEBUG,
                 div_indent: int = DEFAULT_DICT_INDENT
                 ) -> list[str]:
        lines = [f'{k: >{div_indent}s} = {v}' for k, v in data.items()]

        with self._lock:
            if description:
                self.log.log(level, description)
            for line in lines:
                self.log.log(level, line)
            self.log.log(level, '')

        return lines

    def log_json(self, data: dict,
                 description: str = '',
                 level: int = logging.DEBUG,
                 indent=DEFAULT_JSON_INDENT
                 ) -> str:
        txt = json.dumps(data, indent=indent)
        self.log.log(level, f'{description}\n{txt}')
        return txt

    def log_yaml(self, data: dict, description: str = '', level: int = logging.DEBUG) -> str:
        txt = yaml.dump(data)
        self.log.log(level, f'{description}\n{txt}')
        return txt

    def log_and_report_list(self, data: Iterable, description: str = '') -> None:
        self.log_list(data, description, level=logging.INFO)
        allure.attach('\n'.join(data), description, allure.attachment_type.TEXT)

    def log_and_report_dict(self, data: dict, description: str = '', div_indent=DEFAULT_DICT_INDENT) -> None:
        lines = self.log_dict(data, description, level=logging.INFO, div_indent=div_indent)
        allure.attach('\n'.join(lines), description, allure.attachment_type.TEXT)

    def log_and_report_json(self, data: dict, description: str = '', indent=DEFAULT_JSON_INDENT) -> None:
        txt = self.log_json(data, description, level=logging.INFO, indent=indent)
        allure.attach(txt, description, allure.attachment_type.JSON)

    def log_and_report_yaml(self, data: dict, description: str = '') -> None:
        txt = self.log_yaml(data, description, level=logging.INFO)
        allure.attach(txt, description, allure.attachment_type.YAML)

    # can't be typehinted because allure.step uses private module class allure_commons._allure.StepContext
    def log_step(self, title: str):  # type: ignore
        self.log.info(title)
        return allure.step(title)


def quick_logging_setup(fmt: str = '%(asctime)-15s |%(levelname)+8s| %(name)+30s | %(message)s'):
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout, format=fmt)
