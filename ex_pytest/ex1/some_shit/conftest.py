import pytest


def pytest_addoption(parser: pytest.Parser):
    parser.addoption('--stubs', dest='my_stubs', action='store_true', help='Use stubs for ENB, EPC, etc.')
