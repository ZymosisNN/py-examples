import pytest


class Parameter:
    pass


@pytest.fixture(scope='module', params=[Parameter(), Parameter()])
def ololo(request):
    print(request)
    print(request.param)
    return request.param


def test_ololo(ololo):
    print(f'ololo: {ololo}, type: {type(ololo)}')
