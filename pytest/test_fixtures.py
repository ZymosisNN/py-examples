import pytest


@pytest.fixture
def fix_yield():
    print('fix_yield BEGIN')
    yield 'fix_yield RESOURCE'
    return 'fix_yield END'


@pytest.fixture
def fix_no_yield():
    print('fix_no_yield BEGIN')
    return 'fix_no_yield RESOURCE'


def test_func1(fix_yield):
    print(f'test_func works with {fix_yield}')


def test_func2(fix_no_yield):
    print(f'test_func works with {fix_no_yield}')
