from behave import fixture
from behave.runner import Context

__all__ = ['fix1']


@fixture
def fix1(context: Context, param: str):
    print(f'FIXTURE SETUP fix1 {context=}')
    print(f'    {param=}')
    print(f'    {context=}')

    def cleanup():
        print('fix1: context.add_cleanup -> cleanup')

    context.add_cleanup(cleanup)

    yield 'fix1_result'
    print('FIXTURE CLEANUP fix1')
