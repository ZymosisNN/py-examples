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

    def test_2(self, fix_1):
        print(f'test_2 --> {fix_1}')
        assert [1]


@pytest.mark.slow
def test_jopa():
    print('JOPA')

