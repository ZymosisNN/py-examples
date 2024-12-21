import asyncio
import json
from urllib.parse import unquote

import websockets
from pydantic import ValidationError

from ..common import LogMixin, Message


class MMProxyMsgReceiver(LogMixin):
    def __init__(self, url: str, token: str, inbox: asyncio.Queue[Message]):
        super().__init__()
        self._url = url
        self._headers = {'Authorization': f'Bearer {token}'}
        self._inbox = inbox
        self._task: asyncio.Task | None = None

    def start(self):
        if self._task:
            raise Exception('Already started')
        self.log.info('START')
        self._task = asyncio.create_task(self._listen())

    def stop(self):
        if not self._task:
            return
        self.log.info('STOP')
        self._task.cancel()
        self._task = None

    async def _listen(self):
        self.log.info(f'Open WS to {self._url}')
        async with websockets.connect(self._url, self._headers) as ws:
            self.log.info('Start listening MM proxy')
            while True:
                msg_str = await ws.recv()
                self.log.debug(f'RECV: {msg_str}')
                msg_str = unquote(msg_str)
                data = json.loads(msg_str)
                self.log_dict(data, 'Data:')
                try:
                    message = Message.parse_obj(data)
                except ValidationError as err:
                    self.log.error(f'Cannot parse data: {err}')
                else:
                    self.log_dict(message.dict(), 'MM MESSAGE:')
                    await self._inbox.put(message)
