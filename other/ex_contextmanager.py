from contextlib import contextmanager


@contextmanager
def c_manager(obj):
    try:
        print(f'ENTER {obj}')
        yield obj
    except Exception as ex:
        print(ex)
        raise
    finally:
        print('EXIT')


with c_manager('first') as obj:
    print(f'    inside with {obj}')

with c_manager('second') as obj:
    print(f'    inside with {obj}')
