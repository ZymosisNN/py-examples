# For the cases when an argument variable has the same name as a kay in **kwargs
def f1(name, /, **kwargs):
    print(f'name: {name}')
    print(f'kwargs: {kwargs}')


f1('preved', a=2, b=3, c=4, name='medved')


# Arguments after * must be used as named (use case: no default value)
def f2(title, *, first, second):
    print(f'title: {title}')
    print(f'first: {first}')
    print(f'second: {second}')


f2('aaa', first='bbb', second='ccc')
