import pytest


class CustomException(Exception):
    pass


class SutClass:
    def __init__(self):
        self.var = 123

    def raise_exception(self):
        raise CustomException


class TestSut:
    def setup(self):
        self.sut = SutClass()

    def test_1(self, *args, **kwargs):
        print('test_1', args, kwargs)
        with pytest.raises(CustomException):
            self.sut.raise_exception()


@pytest.mark.slow
def test_jopa():
    print('JOPA')

