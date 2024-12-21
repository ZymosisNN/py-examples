import logging


def test_inner_1(top_fixture):
    logging.getLogger('test_inner_1').info(top_fixture)
    assert False
