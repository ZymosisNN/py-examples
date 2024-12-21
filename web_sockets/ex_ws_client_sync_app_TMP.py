import logging
import threading
from datetime import datetime
from enum import Enum

import websocket
from pydantic import BaseModel, ValidationError, Field

from log_mixin import LogMixin
from log_tools import set_format
import websocket
import _thread
import time




class EpcEventType(str, Enum):
    MSG = 'MSG'
    ERROR = 'ERROR'


class EpcEvent(BaseModel):
    type: EpcEventType
    data: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# import rel

def on_message(ws: websocket.WebSocketApp, message):
    logging.info(message)


def on_error(ws, error):
    logging.info(error)


def on_close(ws, close_status_code, close_msg):
    logging.info("### closed ###")


def on_open(ws):
    logging.info("Opened connection")



class EpcSimWSClient(LogMixin):
    def __init__(self, addr: str = 'ws://127.0.0.1'):
        super().__init__()
        self._lock = threading.Lock()
        self._buffer: list[EpcEvent] = []

        self.ws = websocket.WebSocket()
        self._running = True
        self._addr = addr

    def start(self):
        ws = websocket.WebSocketApp(self._addr,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.run_forever()

        self.log.critical('WS status:')
        self.log.critical(self.ws.status)

        self.ws.close()

    def _wait_data(self):
        try:
            data = self.ws.recv()
        except websocket.WebSocketConnectionClosedException:
            self.log.debug('WS closed by server')
            self._running = False
            return 'WS CLOSED'

        self.log.debug(f'RECV: {data}')

        try:
            return EpcEvent.parse_raw(data)
        except ValidationError as e:
            self.log.error(f'Cannot parse data from EPC: {e}')

        return data

    def stop(self):
        self.log.debug('Stop WS')
        self._running = False

    def get_buffer(self):
        with self._lock:
            return self._buffer.copy()


if __name__ == '__main__':
    websocket.enableTrace(True)
    set_format()

    client = EpcSimWSClient()
    logging.info('Start client thread')
    t = threading.Thread(target=client.start)
    t.start()
    t.join()
    logging.info('DONE')
