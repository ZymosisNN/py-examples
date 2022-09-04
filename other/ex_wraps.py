from functools import wraps, WRAPPER_ASSIGNMENTS, WRAPPER_UPDATES


def deco_wraps(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print('Decorators work')
        return f(*args, **kwargs)

    return wrapper


def deco_no_wraps(f):
    def wrapper(*args, **kwargs):
        print('Decorators work')
        return f(*args, **kwargs)

    return wrapper


@deco_wraps
def func_wraps(a: int, b: str) -> list[int, str]:
    """Some docstring"""
    return [a + 10, f'{a} -- {b}']


@deco_no_wraps
def func_no_wraps(a: int, b: str) -> list[int, str]:
    """Some docstring"""
    return [a + 10, f'{a} -- {b}']


for i in WRAPPER_ASSIGNMENTS + WRAPPER_UPDATES:
    print(i, '=', getattr(func_wraps, i))

print('-' * 100)

for i in WRAPPER_ASSIGNMENTS + WRAPPER_UPDATES:
    print(i, '=', getattr(func_no_wraps, i))
