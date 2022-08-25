def decor_maker(before, after):
    print('decor_maker -->')

    def decor(func):
        print('decor -->')

        def wrapper(*args, **kwargs):
            print(f'before: {before}')
            print(f'args: {args}')
            print(f'kwargs: {kwargs}')
            func(*args, **kwargs)
            print(f'after: {after}')

        print('decor <--')
        return wrapper

    print('decor_maker <--')
    return decor


@decor_maker('BEF', 'AFT')
def f(arg1, arg2, kw=None):
    print(f'DECORATED FUNC: f({arg1}, {arg2}, {kw})')


if __name__ == '__main__':
    print('- Script start -')
    f('a', 'b', kw='jopa')
