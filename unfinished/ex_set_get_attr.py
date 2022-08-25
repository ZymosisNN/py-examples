class Some:
    # __slots__ = ['obj_var']
    class_var = 'class_var value'

    def __init__(self):
        self.obj_var = 'self.obj_var value'

    def f1(self):
        print('f1')

    # def __getattr__(self, item):
    #     print('__getattr__')
    #     print(f'    item = {item}')
    #     return 'getattr item value'
    #
    # def __getattribute__(self, item):
    #     print('__getattribute__')
    #     print(f'    item = {item}')
    #     return 'UNKNOWN'

    # def __setattr__(self, key, value):
    #     print('__setattr__')
    #     print(f'    {key} -> {value}')


obj = Some()

# print(f'obj.class_var = {obj.class_var}')
print(f'obj.obj_var = {obj.obj_var}')

obj.f1()
# print(f'obj.hz = {obj.hz}')

print(obj.__dict__)
print(obj.__weakref__)
# print(obj.__slots__)
