from datetime import datetime
from pathlib import Path


def pytest_configure(config):
    timestamp = datetime.strftime(datetime.now(), '%Y-%m-%d_%H-%M-%S')
    config.option.log_file = Path('log') / f'test_{timestamp}.log'

    # suppress predefined loggers
    # for name in CFG['LOGGING']['SUPPRESSED_LOGGERS']:
    #     logger_to_suppress = logging.getLogger(name)
    #     logger_to_suppress.setLevel(logging.ERROR)
