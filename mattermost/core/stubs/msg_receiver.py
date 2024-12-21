import asyncio

from ..msg_receiver import MMProxyMsgReceiver
from ...common import Message


class MMProxyMsgReceiverStub(MMProxyMsgReceiver):
    async def _listen(self):
        self.log.info('Generate MM messages')
        c = 0
        while True:
            message = Message(command=f'cmd #{c}')
            self.log_dict(message.dict(), 'MM MESSAGE:')
            await self._inbox.put(message)
            c += 1
            await asyncio.sleep(3)
