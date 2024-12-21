from behave import *
from behave.runner import Context


@given('common step')
def step_impl(context: Context):
    print(context.text)


@when('common step')
def step_impl(context: Context):
    print(context.text)


@then('common step')
def step_impl(context: Context):
    print(context.text)
