import logging
import sys


def setup_logger(level=logging.DEBUG):
    # fmt = '%(asctime)-15s [%(levelname)-8s] %(processName)s %(process)d %(threadName)-10s %(name)+34s | %(message)s'
    # fmt = '%(asctime)-15s [%(levelname)-8s] %(processName)s, %(threadName)-10s %(name)+25s | %(message)s'
    fmt = '%(asctime)-15s  |%(levelname)-8s| %(name)+35s |  %(message)s'

    # formatter = logging.Formatter(fmt=fmt)
    # sh = logging.StreamHandler(stream=sys.stdout)
    # sh.setLevel(logging.INFO)

    logging.basicConfig(level=level, stream=sys.stdout, format=fmt)
