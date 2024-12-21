from behave.runner import Context
from behave.model import Step, Scenario, Tag, Feature


def before_step(context: Context, step: Step):
    print(f'ENVIRONMENT before_step: {step}')
    print('')


def after_step(context: Context, step: Step):
    print('')
    print(f'ENVIRONMENT after_step: {step}')
    # print(context)


def before_scenario(context: Context, scenario: Scenario):
    print(f'ENVIRONMENT before_scenario: {scenario}, {scenario.tags}')
    # print(context)
    context.cookies = {}


def after_scenario(context: Context, scenario: Scenario):
    print(f'ENVIRONMENT after_scenario: {scenario}')
    # print(context)
    print(f'    {context.cookies=}')


def before_feature(context: Context, feature: Feature):
    print('ENVIRONMENT before_feature:')
    print(f'    {feature}')
    print(f'    tags: {feature.tags}')
    # print(context)


def after_feature(context: Context, feature: Feature):
    print('ENVIRONMENT after_feature:')
    print(f'    {feature}')
    print(f'    tags: {feature.tags}')
    # print(context)


def before_tag(context: Context, tag: Tag):
    print(f'ENVIRONMENT before_tag: {tag}')
    # print(context)


def after_tag(context: Context, tag: Tag):
    print(f'ENVIRONMENT after_tag: {tag}')
    # print(context)


def before_all(context: Context):
    print('ENVIRONMENT before_all:')
    # print(context)


def after_all(context: Context):
    print('ENVIRONMENT after_all:')
    # print(context)
