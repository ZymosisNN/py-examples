import argparse

import uvicorn

from log_cfg import LOG_CONFIG
from app import app

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8080)
parser.add_argument('--host', type=str, default='127.0.0.1')
args = parser.parse_args()

uvicorn.run(app, host=args.host, port=args.port, reload=False, workers=1, log_config=LOG_CONFIG)
