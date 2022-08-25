import yaml
import logging
from logging.config import dictConfig

dictConfig(yaml.safe_load(open('log_cfg.yml')))
log = logging.getLogger()
