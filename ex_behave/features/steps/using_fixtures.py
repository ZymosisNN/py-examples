from behave import *
from behave.runner import Context

from ex_behave.fixtures import fix1


@given('A fixture with {param}')
def step_impl(context: Context, param: str):
    result = use_fixture(fix1, context, param)
    print(result)


@when('feat2')
def step_impl(context: Context):
    pass


@then('feat2')
def step_impl(context: Context):
    pass
