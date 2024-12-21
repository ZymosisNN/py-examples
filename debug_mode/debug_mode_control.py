import logging
from typing import Callable, TypeVar

import yaml

from log_mixin import LogMixin, quick_logging_setup

DecoratedFuncT = TypeVar("DecoratedFuncT", bound=Callable[..., None])

__DEBUG_MODE_OPTS = yaml.safe_load(open('debug_mode.yaml'))


def debug_skip(option: str) -> Callable[[DecoratedFuncT], DecoratedFuncT]:
    def decorator(func: DecoratedFuncT) -> DecoratedFuncT:
        try:
            if __DEBUG_MODE_OPTS['SKIP'][option]:
                def skip(*_, **__) -> None:
                    logging.getLogger('DEBUG_SKIP_CALL').warning(f'# {func.__name__}')
                    return None

                return skip
        except KeyError:
            pass

        return func

    return decorator


class SomeThing(LogMixin):
    @debug_skip('skip_1')
    def method_skip_1(self, arg1, kwarg1='preved'):
        self.log.info(f'call method_skip_1  {arg1}  {kwarg1}')

    @debug_skip('skip_2')
    def method_skip_2(self, arg1, kwarg1='preved'):
        self.log.info(f'call method_skip_2  {arg1}  {kwarg1}')

    @debug_skip('method_skip_undefined')
    def method_skip_undefined(self, arg1, kwarg1='preved'):
        self.log.info(f'call method_skip_undefined  {arg1}  {kwarg1}')


if __name__ == '__main__':
    quick_logging_setup()
    obj = SomeThing()

    obj.method_skip_1(111)
    obj.method_skip_2(222)
    obj.method_skip_undefined(333)
