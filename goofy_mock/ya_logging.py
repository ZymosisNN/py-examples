import json
import logging
import sys
from collections.abc import Mapping
from threading import RLock
from typing import Any, Iterable

import yaml

DEFAULT_DICT_INDENT = 25
DEFAULT_JSON_INDENT = 2

TRACE = 5
logging.addLevelName(TRACE, "TRACE")

_lock = RLock()


class LogMixin:
    """
    Mixin class for entities to have YaLogger
    """

    def __init__(self, subname: str | None = None) -> None:
        name = f'{self.__class__.__name__}{f"({subname})" if subname else ""}'
        self.log = get_logger(name)


class YaLogger(logging.getLoggerClass()):
    """
    Logger class with extra useful methods for quick and nice logs.
    """

    def trace(self, msg: Any) -> None:
        self.log(TRACE, str(msg))

    def log_list(self, data: Iterable, description: str = "", level: int = logging.DEBUG) -> None:
        with _lock:
            if description:
                self.log(level, description)

            for i in data:
                self.log(level, f"    {i}")
            self.log(level, "")

    def log_dict(self, data: Mapping,
                 description: str = "",
                 level: int = logging.DEBUG,
                 key_width: int = DEFAULT_DICT_INDENT
                 ) -> list[str]:
        lines = [f"{str(k): >{key_width}s} = {str(v)}" for k, v in data.items()]

        with _lock:
            if description:
                self.log(level, description)
            for line in lines:
                self.log(level, line)
            self.log(level, "")

        return lines

    def log_json(self, data: dict,
                 description: str = "",
                 level: int = logging.DEBUG,
                 indent: int = DEFAULT_JSON_INDENT
                 ) -> str:
        txt = json.dumps(data, indent=indent)
        self.log(level, f"{description}\n{txt}")
        return txt

    def log_yaml(self, data: dict, description: str = "", level: int = logging.DEBUG) -> str:
        txt = yaml.dump(data)
        self.log(level, f"{description}\n{txt}")
        return txt

    # def log_and_report_list(self, data: Iterable, description: str = '') -> None:
    #     self.log_list(data, description, level=logging.INFO)
    #     allure.attach('\n'.join(data), description, allure.attachment_type.TEXT)
    #
    # def log_and_report_dict(self, data: dict, description: str = '', div_indent: int = DEFAULT_DICT_INDENT) -> None:
    #     lines = self.log_dict(data, description, level=logging.INFO, key_width=div_indent)
    #     allure.attach('\n'.join(lines), description, allure.attachment_type.TEXT)
    #
    # def log_and_report_json(self, data: dict, description: str = '', indent: int = DEFAULT_JSON_INDENT) -> None:
    #     txt = self.log_json(data, description, level=logging.INFO, indent=indent)
    #     allure.attach(txt, description, allure.attachment_type.JSON)
    #
    # def log_and_report_yaml(self, data: dict, description: str = '') -> None:
    #     txt = self.log_yaml(data, description, level=logging.INFO)
    #     allure.attach(txt, description, allure.attachment_type.YAML)
    #
    # # can't be typehinted because allure.step uses private module class allure_commons._allure.StepContext
    # def log_step(self, title: str):  # type: ignore
    #     self.info(title)
    #     return allure.step(title)


logging.setLoggerClass(YaLogger)


# TODO: find solution without type mismatch
def get_logger(name: str = '', subname: str | None = None) -> YaLogger:
    name = name.strip() or ' '
    if name == 'root':
        raise ValueError('It is prohibited to use logger name "root", because in this case '
                         'logging module returns logger, not YaLogger')
    log: YaLogger = logging.getLogger(f'{name}{f"({subname})" if subname else ""}')
    return log


def set_stdout_logging(fmt: str = "%(asctime)-15s |%(levelname)+8s| %(name)+20s | %(message)s",
                       level: int = TRACE
                       ) -> None:
    logging.basicConfig(level=level, stream=sys.stdout, format=fmt, datefmt="%Y-%m-%d %H:%M:%S")


def get_simple_logger(name: str = '', name_column_size: int = 20) -> YaLogger:
    """
    Helper function that creates a YaLogger and configures logging.
    Format is set during the first call and not changed on next calls.
    Logger's name column is printed only if they were defined on the first call.
    """
    log = get_logger(name)
    fmt = '%(levelname)+8s| %(message)s'
    if name:
        fmt = f'%(name)+{name_column_size}s |{fmt}'
    set_stdout_logging(fmt)

    return log


def step(title: str = '') -> None:
    log = get_logger()
    with _lock:
        log.info("")
        log.info(title.center(100, "-"))
        log.info("")


def log_dict(data: dict,
             description: str = "", *,
             key_width: int = 20,
             log_name: str = None,
             level: int = logging.INFO
             ) -> None:
    log = get_logger(log_name)
    log.log_dict(data, description, level, key_width)


def log_list(data: Iterable,
             description: str = None, *,
             log_name: str = None,
             level=logging.DEBUG
             ) -> None:
    log = get_logger(log_name)
    log.log_list(data, description, level)


def log_json(data: dict,
             description: str = None, *,
             log_name: str = None,
             level=logging.DEBUG
             ) -> None:
    log = get_logger(log_name)
    log.log_json(data, description, level)


if __name__ == '__main__':
    """
    Simple demo of ya_logging module usage
    """
    speaker = get_simple_logger('---Explanation---')
    speaker.info('Function step() as silent 3 lines separator:')
    step()

    speaker.info('Function step("some title"):')
    step('some title')

    speaker.info('Method log_dict(dict_obj) prints given Mapping object')
    dict_logger = get_simple_logger('dict_logger')
    dict_logger.log_dict({'some key': 'some value', 'default level is "DEBUG"': logging.DEBUG},
                         'Data description:', key_width=40)

    dict_logger.log_dict({'dict without description': 1, 'and default indent': 2}, level=logging.WARNING)

    speaker.info('Method log_list(list_obj) prints given Iterable object')
    list_logger = get_simple_logger('list_logger')
    list_logger.log_list([1, 2, 3], description='Description is also optional:', level=logging.ERROR)

    speaker.info('YaLogger is an extended logging.Logger class. Levels in decreasing order:')
    levels = get_simple_logger('levels')
    levels.critical('logger.critical() - top level')
    levels.fatal('logger.fatal() == logger.critical()')
    levels.exception('logger.exception() - ERROR level, use it to print exceptions')
    try:
        raise RuntimeError('Your exception message')
    except Exception as e:
        levels.exception(e)
    levels.error('logger.error()')
    levels.info('logger.info()')
    levels.debug('logger.debug()')
    levels.trace(f'YaLogger.trace() - this is custom YaLogger log level "TRACE"={TRACE}, lower than DEBUG')
