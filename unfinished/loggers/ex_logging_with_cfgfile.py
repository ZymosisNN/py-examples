import logging.config


logging.config.fileConfig('logging.cfg')

log1 = logging.getLogger('log1')
log2 = logging.getLogger('log2')

logging.info('some message from root')

log1.info('some message from log1')
log2.info('some message from log2')

log1.exception('aaaaa')
