import logging
import logging.config


logging.config.fileConfig('logging_test.cfg')

logging.getLogger('unknown').error('unknown logger')
logging.getLogger('log1').info('log1 logger')
logging.getLogger('common').info('common logger')
logging.getLogger('common.1').info('common.1 logger')

