from typing import Any

from ..result_sender import MMServiceResultSender


class MMServiceResultSenderStub(MMServiceResultSender):
    async def _send(self, url: str, data: Any):
        self.log.info('STUB send:')
        self.log.info(f'    URL : {url}')
        self.log.info(f'    Data: {data}')
