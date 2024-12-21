import pytest

from ex_pytest.ex_coverage.sample_class import MySUT


@pytest.fixture
def sut():
    return MySUT()


def test_1(sut):
    assert sut.a == 'aaa'
    assert sut.b == 123


def test_2(sut):
    assert sut.f1() == ['aaa', 123]


def test_3(sut):
    assert sut.f2(True) == ['aaa', 123, True]
