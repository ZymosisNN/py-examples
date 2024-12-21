import enum
import json
import logging
from abc import ABC, abstractmethod
from threading import RLock
from typing import Any, NamedTuple, Dict, Optional, Iterable

TRACE = 5
logging.addLevelName(TRACE, 'TRACE')


class ContentType(enum.IntEnum):
    NONE = enum.auto()
    TEXT = enum.auto()
    LIST = enum.auto()
    DICT = enum.auto()
    BINARY_FILEPATH = enum.auto()


class ServiceRequest(NamedTuple):
    """
    data is sent to service with service_name
    if response_service_name is None:
        future of service task is returned
    else:
        service result is put into response_data['content'] and sent to response_service
        a future of response_service task is returned
    """
    service_name: str
    data: dict
    response_service_name: Optional[str] = None
    response_data: Optional[Dict] = None


class ServiceResult(NamedTuple):
    service_name: str
    content: Any = None
    content_type: ContentType = ContentType.NONE
    error: Optional[str] = None


class LogMixin:
    _lock = RLock()

    def __init__(self, subname: str = None):
        name = self.__class__.__name__ + (f'({subname})' if subname else '')
        self._log = logging.getLogger(name)

    def trace(self, msg: Any):
        self._log.log(TRACE, msg)

    def log_list(self, data: Iterable, description: str = ''):
        with self._lock:
            if description:
                self._log.debug(description)

            for i in data:
                self._log.debug(f'    {i}')
            self._log.debug('')

    def log_dict(self, data: Dict, description: str = ''):
        with self._lock:
            if description:
                self._log.debug(description)

            for k, v in data.items():
                self._log.debug(f'{k: >25s} = {v}')
            self._log.debug('')

    def log_json(self, data: Dict, description: str = ''):
        self._log.debug(f'{description}\n{json.dumps(data, indent=4)}')

    def log_with_limit(self, content: Any, description: str = '', max_chars=10000):
        content = str(content)
        if len(content) > max_chars:
            content = f'{content[:max_chars]}\n\n...too big output, cut off here...\n'
        self._log.debug(f'{description}\n{content}')


class NameAndLogMixin(LogMixin):
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    @property
    def name(self):
        return self._name


class AbstractService(ABC, NameAndLogMixin):
    @abstractmethod
    def exec(self, data: Dict) -> ServiceResult: ...


class ChatOpsError(Exception):
    pass
