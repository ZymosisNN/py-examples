class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            print(f'MetaSingleton __call__ cls: {cls}')
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Parent(metaclass=MetaSingleton):
    def __init__(self):
        print('Parent __init__')


class Child(Parent):
    def __init__(self):
        super().__init__()
        print('Child __init__')
        self.v = 1234567890


p1 = Parent()
c1 = Child()

p2 = Parent()
c2 = Child()

print(p1)
print(c1)
print(p2)
print(c2)
print(c1.v)
