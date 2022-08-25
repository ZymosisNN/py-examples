class Decor:
    def __init__(self, cls):
        print(f'Decor __init__, {cls=}')
        self._cls = cls

    def __call__(self, *args, **kwargs):
        print(f'Decor {args=}')
        print(f'Decor {kwargs=}')
        return self._cls(*args, **kwargs)


@Decor
class Jopa:
    def __init__(self, *args, **kwargs):
        print('Jopa __init__')
        print(f'Jopa {args=}')
        print(f'Jopa {kwargs=}')


obj = Jopa(1, 2, kw1='Z', kw2='X')
print(obj)
