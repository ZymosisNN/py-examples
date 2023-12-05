import json
import logging
import sys
from threading import RLock
from typing import Iterable

TRACE = 5
logging.addLevelName(TRACE, 'TRACE')

_lock = RLock()


def set_format(fmt: str = '%(asctime)-15s |%(levelname)+8s| %(name)+30s | %(message)s') -> None:
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout, format=fmt)


def step(title: str) -> None:
    log = logging.getLogger(' ')
    with _lock:
        log.info('')
        log.info(title.center(100, '-'))
        log.info('')


def log_dict(data: dict,
             title: str = None,
             *,
             key_width: int = 20,
             log_name: str = None,
             level: int = logging.INFO
             ) -> None:
    log = logging.getLogger(log_name)
    with _lock:
        if title:
            log.log(level, title)

        for k, v in data.items():
            log.log(level, f'{k: >{key_width}s} = {v}')

        log.log(level, '')


def log_list(data: Iterable,
             title: str = None,
             *,
             log_name: str = None,
             level=logging.DEBUG
             ) -> None:
    log = logging.getLogger(log_name)
    with _lock:
        if title:
            log.log(level, title)

        for i in data:
            log.log(level, f'    {i}')

        log.log(level, '')


def log_json(data: dict,
             title: str = None,
             *,
             log_name: str = None,
             level=logging.DEBUG
             ) -> None:
    log = logging.getLogger(log_name)
    log.log(level, f'{title}\n{json.dumps(data, indent=4)}')
