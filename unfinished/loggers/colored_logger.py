import coloredlogs
import logging
import sys

# import ctypes
# kernel32 = ctypes.windll.kernel32
# kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def enable_colors(level=logging.DEBUG):
    fmt = '%(asctime)-15s [%(levelname)-8s] %(processName)s %(threadName)-10s %(name)-34s | %(message)s'
    # fmt = '[%(levelname)-8s] %(message)s'
    # fmt = '%(message)s'
    styles = 'message=white'
    coloredlogs.DEFAULT_FIELD_STYLES.update(coloredlogs.parse_encoded_styles(styles))
    coloredlogs.install(level=level, fmt=fmt, stream=sys.stdout)


if __name__ == '__main__':

    LOG = logging.getLogger('TEST')
    enable_colors()

    LOG.debug("this is a debugging message")
    LOG.info("this is an informational message")
    LOG.warning("this is a warning message")
    LOG.error("this is an error message")
    LOG.critical("this is a critical message")
