from functools import partial
import logging
import sys

from loguru import logger

LOGURU_DEFAULT_FMT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')

    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | {level.icon} <lvl>{level: <8}</> | <cyan>{name: >20}</>  <lvl>{message}</>"
    logger.remove()
    logger.add(sys.stderr, format=fmt, level='TRACE', enqueue=True)

    # Enable color tags
    logger = logger.opt(colors=True)
    logger.opt = partial(logger.opt, colors=True)

    logger.trace('trace')
    logger.debug('debug')
    logger.info('info')
    logger.success('success')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')

    new_level = logger.level('SNAKY', no=38, color='<yellow>', icon='🐍')
    logger.log('SNAKY', 'Here we go!')

    logger.debug('preved <G>medved</>')

    try:
        raise RuntimeError('test exception')
    except RuntimeError as e:
        logger.exception(e)

    # For logging support
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    log = logging.getLogger('StdLogger')
    log.debug('message from standard logger')
