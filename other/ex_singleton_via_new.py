class Parent:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            print('Parent __new__', cls)
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

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
