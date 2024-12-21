import pytest


@pytest.fixture
def outside_fixture_1():
    print('RUN outside_fixture_1')
    return 'outside_fixture_1 result'
