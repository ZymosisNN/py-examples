import logging
import threading
from datetime import datetime
from enum import Enum
from urllib.parse import urlparse

import websocket
from pydantic import BaseModel, ValidationError, Field

from log_mixin import LogMixin
from log_tools import set_format


class EpcEventType(str, Enum):
    MESSAGE = 'message'
    SCRIPT_FINISHED = 'scriptFinished'
    SCRIPT_ERROR = 'scriptError'


class EpcEvent(BaseModel):
    event_type: EpcEventType = Field(alias='eventType')
    data: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EpcSimWSClientThread(threading.Thread, LogMixin):
    def __init__(self, addr: str):
        threading.Thread.__init__(self)
        LogMixin.__init__(self, subname=urlparse(addr).hostname)

        self._lock = threading.Lock()
        self._buffer: list[EpcEvent] = []

        self.log.info(f'Open WS to EPC ({addr})')
        self._ws = websocket.WebSocket()
        self._ws.connect(addr)

    def run(self):
        self.log.info('Start listening EPC')

        while self._ws.connected:
            try:
                data = self._ws.recv()
            except websocket.WebSocketConnectionClosedException:
                break

            self.log.debug(f'RECV: {data}')
            if not data:
                continue

            try:
                epc_event = EpcEvent.parse_raw(data)
            except ValidationError as e:
                self.log.error(f'Cannot parse data from EPC: {e}')
            else:
                with self._lock:
                    self._buffer.append(epc_event)

        self.log.info('WS to EPC is closed')

    def stop(self):
        if self._ws.connected:
            self.log.debug('Close WS to EPC')
            self._ws.close()

    def get_buffer(self):
        with self._lock:
            return self._buffer.copy()


if __name__ == '__main__':
    import time

    set_format()

    # addr = 'ws://127.0.0.1:446'
    addr = 'ws://10.78.225.49:446'
    # addr = 'ws://172.31.144.117:446'
    client_thread = EpcSimWSClientThread(addr)
    client_thread.start()

    time.sleep(3)
    client_thread.stop()
    client_thread.join()

    logging.info('DONE')
    b = client_thread.get_buffer()
    client_thread.log_list(b, 'Buffer:')
