class MyException(Exception):
    pass


def raise_no_from():
    try:
        raise MyException('Root cause')
    except MyException:
        raise RuntimeError('Last exception')


def raise_with_from():
    try:
        raise MyException('Root cause')
    except MyException as e:
        raise RuntimeError('Last exception') from e


for f in (raise_no_from, raise_with_from):
    try:
        f()
    except Exception as exception:
        print(f'{exception=}')
        print(f'{exception.__cause__=}')
        print(f'{exception.__context__=}')
        print('')

