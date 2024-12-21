from behave import *
from behave.runner import Context


@given('param1 is {p1} and param2 is {p2}')
def step_impl(context: Context, p1: str, p2: str) -> None:
    print(f'GIVEN {p1=}  {p2=}')


@when('having table')
def step_impl(context: Context) -> None:
    print('WHEN having table:')
    for i in context.table:
        print(i)


@then('all params {p1} {p2} {p3}')
def step_impl(context: Context, p1: str, p2: str, p3: str) -> None:
    print(f'THEN {p1=} {p2=} {p3=}')
