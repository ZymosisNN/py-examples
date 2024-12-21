from behave.runner import Context
from behave import *


@given('Working entity with {p}')
def step_impl(context: Context, p):
    print(p)
    for i in context.table:
        print(i)
    context.execute_steps('''
    when Some action
    and Some action
    given Some action
    but Some action
    ''')


@when('Performs operation with {p1}, {p2}')
def step_impl(context: Context, p1, p2):
    print(f'{p1=}  {p2=}')


@then('Result is "{param3}"')
def step_impl(context: Context, param3):
    print(f'{param3=}')
    print(context.response)


@when('Some action')
def step_impl(context: Context):
    print('execute_steps called WHEN "Some action"')


@given('Some action')
def step_impl(context: Context):
    print('execute_steps called GIVEN "Some action"')
