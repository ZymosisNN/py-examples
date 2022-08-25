from functools import partial


def some_func(arg1, arg2, karg='DEFAULT'):
    print(f'arg1={arg1}, arg2={arg2}, karg={karg}')


# some_func(1, 2, 'jopa')

# new_func = partial(some_func, 111, karg='NEW')
# new_func(222)
# new_func2 = partial(some_func, arg2=22, karg='NEW')
# new_func2(11)


def nextId(idx, amount):
    end = idx + amount
    while idx < end:
        yield idx
        idx += 1


f = nextId(10, 5)

print(next(f))
print(next(f))
