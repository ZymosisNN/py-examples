import logging
import pytest
import sys


@pytest.fixture
def fix_1():
    logging.info('RUN fix_1')
    return '---->fix_1'


@pytest.fixture
def fix_2():
    logging.info('RUN fix_2')
    return '---->fix_2'


def test_jopa(fix_1, fix_2):
    logging.info(f'{fix_1=}  {fix_2=}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')
