from behave import *
from behave.runner import Context

use_step_matcher("parse")


@step("two parameters {a} {b}")
def step_impl(context, a, b):
    print(f'{a=}; {b=}')


@when("set context {key} = {value}")
def step_impl(context: Context, key: str, value: str):
    """
    :type key: str
    :type value: str
    :type context: behave.runner.Context
    """
    print(f'SET {key}={value}')
    context.cookies[key] = value


@then("get context {key}")
def step_impl(context: Context, key: str):
    """
    :type key: str
    :type context: behave.runner.Context
    """
    print(f'GET {key}')
    value = context.cookies[key]
    print(f'    {value=}')
