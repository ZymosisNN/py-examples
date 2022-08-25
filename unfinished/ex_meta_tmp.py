import asyncio
from typing import Type
from common_bases import LogMixin
import logging

import sys
logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                    format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')


class AutofillOuts(type):
    log = logging.getLogger('NodeMeta')
    _annotated_outs: dict[str, set] = {}
    _optional_outs: dict[str, set] = {}

    @classmethod
    def add_outs(mcs, user_class: Type, class_attrs: dict):
        class_name = user_class.__name__
        parent_name = user_class.__base__.__name__

        parent_outs = mcs._optional_outs.get(parent_name, set())
        mcs._optional_outs[class_name] = parent_outs | {k for k in class_attrs if k.startswith('out_')}

        parent_outs = mcs._annotated_outs.get(parent_name, set())
        annotations = class_attrs.get('__annotations__', {})
        mcs._annotated_outs[class_name] = parent_outs | {k for k in annotations if k.startswith('out_')}
        mcs._annotated_outs[class_name] -= mcs._optional_outs[class_name]

        return mcs._annotated_outs[class_name], mcs._optional_outs[class_name]

    def __init__(cls, class_name, parents, attributes):
        cls.log.debug(f'INIT: {cls=} {class_name=} {parents=} {attributes=}')
        cls.__annotated_outs, cls.__optional_outs = AutofillOuts.add_outs(cls, attributes)
        cls.log.debug(f'{cls.__annotated_outs=}')
        cls.log.debug(f'{cls.__optional_outs=}')
        cls.log.debug('')
        super().__init__(class_name, parents, attributes)

    def __call__(cls, *args, **kwargs):
        cls.log.debug(f'CALL: {cls=} {args=} {kwargs=}')
        cls.log.debug(f'meta kw: {kwargs}')
        cls.log.debug(f'__annotation_outs: {cls.__annotated_outs}')

        obj = super().__call__(*args, **kwargs)
        for out in cls.__annotated_outs:
            try:
                setattr(obj, out, kwargs[out])
            except KeyError as ex:
                raise RuntimeError(f'"{out}" must be defined during creating "{cls.__name__}".'
                                   f' Mandatory attrs: {cls.__annotated_outs}') from ex

        cls.log.debug(f'obj: {obj}')
        cls.log.debug(f'cls dict: {cls.__dict__}')
        cls.log.debug(f'obj dict: {obj.__dict__}')
        kw_outs = {k: kwargs[k] for k in cls.__optional_outs if k.startswith('out_') and k in kwargs}
        obj.__dict__.update(kw_outs)

        cls.log.debug('')
        return obj


class SuperBase(LogMixin, metaclass=AutofillOuts):
    out_jopa = 'ololo'


class TestBase(SuperBase):
    out_1: str
    out_2 = 'TestBase out_2'


class TestBase2(TestBase):
    out_11: str
    out_21 = 'TestBase2 out_21'


class Test(TestBase2):
    out_3: str
    out_4 = 'Test out_4'
    out_5: str = 'Test out_5'

    # def __init__(self, a, b, *, out_3=None, out_4=None, out_5=None):
    def __init__(self, a, b, **kwargs):
        super().__init__()
        self._log.debug(f'locals={locals()}')
        # print(f'{self.out_1=}')
        self._log.debug(f'{self.out_2=}')
        # print(f'{self.out_3=}')
        self._log.debug(f'{self.out_4=}')
        self._log.debug(f'{self.out_5=}')


print('-' * 100)
a = Test(1, 2, out_1='OUT_1', out_3='OUT_3', out_5='OUT_5', out_11='OUT_11', out_2='SUPER-OUT-2')
print('-' * 100)
print(a.__dict__)

# print([x for x in dir(a) if not callable(getattr(a, x))])

exit(0)


class Deriv1(metaclass=AutofillOuts):
    out_1: str
    out_2: str
    out_3 = '333'
    out_4 = '444'

    def __new__(cls, *args, **kwargs):
        print(f'Deriv1 new dict: {cls.__dict__}')
        print(super)
        print(super())
        return super().__new__(cls, args, kwargs)


class Deriv2(Deriv1):
    out_jopa: str

    def __new__(cls, *args, **kwargs):
        print(f'Deriv2 new dict: {cls.__dict__}')
        return super().__new__(cls, args, kwargs)


j = Deriv1(preved='medved', out_1='zzz', out_2='xxx', out_3='ccc', out_11='JOPAAAA')
j = Deriv2(preved='medved', out_1='zzz', out_2='xxx', out_3='ccc', out_jopa='JOPAAAA')

exit(0)


flag = False


async def a():
    global flag
    print('enter a')
    for i in range(10):
        print(f'a:{i}')
        if i > 5:
            flag = True
        await asyncio.sleep(.05)
    print('exit a')
    return 'a done'


def b():
    print('enter b')
    while not flag:
        print('b waits...')
        yield
    print('exit b')
    return 'b done'


async def main():
    global flag
    tasks = [
        asyncio.create_task(a()),
        asyncio.create_task(b()),
    ]

    for i in range(10):
        print(f'main:{i}')
        if i > 5:
            flag = True
        await asyncio.sleep(.1)

    res = await asyncio.gather(*tasks)
    print(f'RESULTS: {res}')


if __name__ == '__main__':
    asyncio.run(main())
