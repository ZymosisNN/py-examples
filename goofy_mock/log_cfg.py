import os
from pathlib import Path

import yaml

if log_cfg_path := os.environ.get('YATI_LOG_CFG'):  # User defined logging config
    cfg_file = Path(log_cfg_path).resolve()
    try:
        LOG_CONFIG = yaml.safe_load(cfg_file.open())

    except FileNotFoundError:
        raise RuntimeError(f'Env var YATI_LOG_CFG points to non existing file: {cfg_file}')

    except yaml.YAMLError:
        raise RuntimeError(f'Env var YATI_LOG_CFG points to unparseable logging config: {cfg_file}')

    print(f'Using logging config: {cfg_file}')

else:  # Default logging config
    LOG_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)-15s |%(levelname)+8s| %(name)+25s | %(message)s"},
            "access": {"format": "%(asctime)-15s |%(levelname)+8s| %(name)+25s | %(message)s"},
        },
        "handlers": {
            "default": {"formatter": "default", "class": "logging.StreamHandler", "stream": "ext://sys.stderr"},
            "access": {"formatter": "access", "class": "logging.StreamHandler", "stream": "ext://sys.stdout"},
        },
        "loggers": {
            "uvicorn.error": {"level": "INFO", "handlers": ["default"], "propagate": False},
            "uvicorn.access": {"level": "INFO", "handlers": ["access"], "propagate": False},
            "hpack": {"level": "INFO", "handlers": ["default"], "propagate": False},
            "paramiko.transport": {"level": "INFO", "handlers": ["default"], "propagate": False},
        },
        "root": {"level": "INFO", "handlers": ["default"], "propagate": False},
    }
