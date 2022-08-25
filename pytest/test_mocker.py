import pytest

try:
    import mock  # fails on Python 3
except ImportError:
    from unittest import mock


def first_test_fn():
    return 42


def another_test_fn():
    return 42


class TestMockerFixture(object):
    """This is best; the mocker fixture reduces boilerplate and
    stays out of the declarative pytest syntax.
    """

    @pytest.mark.xfail(strict=True, msg="We want this test to fail.")
    def test_mocker(self, mocker):
        mocker.patch("mocker_over_mock.another_test_fn", return_value=84)
        assert another_test_fn() == 84
        assert False

    def test_mocker_follow_up(self):
        assert another_test_fn() == 42

    @pytest.fixture
    def mock_fn(self, mocker):
        return mocker.patch("mocker_over_mock.test_basic.another_test_fn", return_value=84)

    def test_mocker_with_fixture(self, mock_fn):
        assert another_test_fn() == 84
