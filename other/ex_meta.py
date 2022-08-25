class Meta1(type):
    def __new__(mcs, class_name, parents, attrs):
        print(f'Meta1 __new__')
        print(f'           mcs: {mcs}')
        print(f'    class_name: {class_name}')
        print(f'       parents: {parents}')
        print(f'         attrs: {attrs}')
        return super().__new__(mcs, class_name, parents, attrs)

    def __call__(cls, *args, **kwargs):
        print(f'Meta1 __call__')
        print(f'       cls: {cls}')
        print(f'      args: {args}')
        print(f'    kwargs: {kwargs}')
        return super().__call__(*args, **kwargs)


class Meta2(Meta1):
    def __new__(mcs, class_name, parents, attrs):
        print(f'Meta2 __new__')
        print(f'           mcs: {mcs}')
        print(f'    class_name: {class_name}')
        print(f'       parents: {parents}')
        print(f'         attrs: {attrs}')
        return super().__new__(mcs, class_name, parents, attrs)

    def __call__(cls, *args, **kwargs):
        print(f'Meta2 __call__')
        print(f'       cls: {cls}')
        print(f'      args: {args}')
        print(f'    kwargs: {kwargs}')
        return super().__call__(*args, **kwargs)


class Parent1:
    pass


class Parent2:
    pass


class Child(Parent1, metaclass=Meta1):
    def __init__(self, arg, kwarg=None):
        self.arg = arg
        self.kwarg = kwarg
        print('Child __init__')


print('-' * 100)


class NextChild(Child, Parent2, metaclass=Meta2):
    def __init__(self, arg, kwarg=None):
        super().__init__(arg, kwarg)
        print('NextChild __init__')


print('=' * 100)


Child(111, kwarg='jopa')
print('=' * 100)
NextChild(222, kwarg='derived jopa')
