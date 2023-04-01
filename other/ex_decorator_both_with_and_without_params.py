from functools import wraps


# MetaDecorator for decorator
def meta_decor(decor_func):
    # Decorating a decorator (func) during module import
    print(f'[meta_decor]  {decor_func=}')

    @wraps(decor_func)
    def wrap(*args, **kwargs):
        if len(args) == 1 and not kwargs and callable(args[0]):
            # Decorator used simply: @func
            print(f'[meta_decor]  wrap callable {decor_func}  {args=}  {kwargs=}')
            return decor_func(args[0])

        # Decorator used this way: @func(*args, **kwargs)
        def sub_wrap(func):
            print(f'[sub_wrap]  {func=}')
            return decor_func(func, *args, **kwargs)

        print(f'[meta_decor]  wrap NON callable {decor_func}  {args=}  {kwargs=}')
        return sub_wrap

    return wrap


print('=== Use @meta_decor ===')


@meta_decor
def decor(func, decor_param=1):
    @wraps(func)
    def wrap(*args, **kwargs):
        print(f'[decor]  call {func.__name__}    {args=}  {kwargs=}')
        return func(*args, **kwargs)

    print(f'[decor]  wrapping  {func=}  {decor_param=}')
    return wrap


print('=== Use @decor ===')


@decor
def some_func(*args, **kwargs):
    print(f'>>>> some_func  {args=}  {kwargs=}')


print('=== User @decor(something) ===')


@decor()
def some_func2(*args, **kwargs):
    print(f'>>>> some_func  {args=}  {kwargs=}')


print('=== RUN ===')
some_func(1, 2, a=3)
some_func2(11, 22, a=33)
