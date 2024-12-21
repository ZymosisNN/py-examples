import asyncio
from typing import Any

from aiohttp import client

from ..common import LogMixin, ServiceResult


class MMServiceResultSender(LogMixin):
    def __init__(self, outbox: asyncio.Queue[ServiceResult]):
        super().__init__()
        self._outbox = outbox
        self._task: asyncio.Task | None = None

    def start(self):
        if self._task:
            raise Exception('Already started')
        self.log.info('START')
        self._task = asyncio.create_task(self._consume_queue())

    def stop(self):
        if not self._task:
            return
        self.log.info('STOP')
        self._task.cancel()
        self._task = None

    async def _consume_queue(self):
        self.log.info('Start sending results to MM proxy')
        while True:
            srv_result = await self._outbox.get()
            self.log.info(f'Send result: {srv_result}')
            asyncio.create_task(self._send(url=srv_result.mm_msg.url,
                                           data=srv_result.result))
            self._outbox.task_done()

    async def _send(self, url: str, data: Any):
        async with client.ClientSession() as session, session.post(url, data=data) as rsp:
            txt = await rsp.text()
            self.log.info(f'Send status: {rsp.status}')
            self.log.info(f'Send answer: {txt}')
