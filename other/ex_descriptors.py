class Descr:
    def __init__(self, name, value):
        print('__init__')
        print(f'    NEW "{name}" = "{value}"')
        self.name = name
        self.value = value

    def __get__(self, obj, obj_type):
        print('__get__')
        print(f'    {self.name}: {self.value}')
        print(f'    obj = {obj}')
        print(f'    obj_type = {obj_type}')
        return self.value

    def __set__(self, obj, value):
        print('__set__')
        print(f'    {self.name} -> {value}')
        print(f'    obj = {obj}')
        self.value = value

    def __delete__(self, obj):
        print('__del__')
        print(f'    obj = {obj}')


class Some:
    var = Descr('JopaVar', 0)  # Descriptor must be static

    def __init__(self):
        self.var = 'Constructor value'


obj = Some()
print(f'obj.var = {obj.var}')

obj.var = 1
print(f'obj.var = {obj.var}')

del obj.var
print(f'obj.var = {obj.var}')
