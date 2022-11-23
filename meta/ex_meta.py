import logging

from log_tools import set_format, step, log_dict

set_format('%(name)+30s |  %(message)s')


class Meta1(type):
    def __new__(mcs, class_name, parents, attrs):
        data = {'msc': mcs, 'class_name': class_name, 'parents': parents, 'attrs': attrs}
        log_dict(data, f'Params for {mcs.__name__}:', log_name=f'{mcs.__name__}.__new__')
        return super().__new__(mcs, class_name, parents, attrs)

    def __call__(cls, *args, **kwargs):
        data = {'cls': cls, 'args': args, 'kwargs': kwargs}
        log_dict(data, 'Params for Meta1:', log_name='Meta1.__call__')
        return super().__call__(*args, **kwargs)


class Meta2(Meta1):
    def __call__(cls, *args, **kwargs):
        data = {'cls': cls, 'args': args, 'kwargs': kwargs}
        log_dict(data, 'Params for Meta2:', log_name='Meta2.__call__')
        return super().__call__(*args, **kwargs)


class Parent1:
    pass


class Parent2:
    pass


step('Define "Child" class')


class Child(Parent1, metaclass=Meta1):
    def __init__(self, arg, kwarg=None):
        self.arg = arg
        self.kwarg = kwarg
        log = logging.getLogger('Child.__init__')
        log.info('DONE')

    def __str__(self):
        return f'{self.__class__.__name__}(arg: "{self.arg}", kwarg: "{self.kwarg}")'


step('Define "NextChild" class')


class NextChild(Child, Parent2, metaclass=Meta2):
    def __new__(cls, *args, **kwargs):
        log = logging.getLogger('NextChild.__new__')
        log.info(f'{cls=}')
        log.info(f'{args=}, {kwargs=}')
        obj = Child.__new__(cls)
        log.info(f'CREATED: {obj=}')
        return obj

    def __init__(self, arg, kwarg=None):
        log = logging.getLogger('NextChild.__init__')
        log.info(f'{arg=}, {kwarg=}')
        log.info('DONE')
        super().__init__(arg, kwarg)


step('Create Child instance')
obj = Child(111, kwarg='jopa')
logging.getLogger().info(f'Created object = {obj}')

step('Create NextChild instance')
obj = NextChild(222, kwarg='derived jopa')
logging.getLogger().info(f'Created object = {obj}')
