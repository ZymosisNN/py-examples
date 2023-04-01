import json
import logging
import sys
from threading import RLock
from typing import Iterable, Any

TRACE = 5
logging.addLevelName(TRACE, 'TRACE')


class LogMixin:
    """
    Mixin class for entities which write logs. It contains useful methods for quick and nice logs.
    """
    __lock = RLock()

    def __init__(self, subname: str = None):
        name = f'{self.__class__.__name__}{f"({subname})" if subname else ""}'
        self.log = logging.getLogger(name)

    def trace(self, msg: Any):
        self.log.log(TRACE, msg)

    def log_list(self, data: Iterable, description: str = '', level=logging.DEBUG):
        with self.__lock:
            if description:
                self.log.log(level, description)

            for i in data:
                self.log.log(level, f'    {i}')
            self.log.log(level, '')

    def log_dict(self, data: dict, description: str = '', level=logging.DEBUG):
        with self.__lock:
            if description:
                self.log.log(level, description)

            for k, v in data.items():
                self.log.log(level, f'{k: >25s} = {v}')
            self.log.log(level, '')

    def log_json(self, data: dict, description: str = '', level=logging.DEBUG):
        self.log.log(level, f'{description}\n{json.dumps(data, indent=4)}')


def quick_logging_setup(fmt: str = '%(asctime)-15s |%(levelname)+8s| %(name)+30s | %(message)s'):
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout, format=fmt)
