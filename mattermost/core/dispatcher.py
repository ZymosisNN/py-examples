import asyncio
import contextvars
from asyncio import Queue

from ..common import LogMixin, SlashService, Message, ServiceResult, ServiceResultStatus


class Dispatcher(LogMixin):
    def __init__(self):
        super().__init__()
        self._services: dict[str, SlashService] = {}
        self._inbox: Queue[Message] = Queue()
        self._outbox: Queue[ServiceResult] = Queue()
        self._task: asyncio.Task | None = None

    def register_srv(self, *services: SlashService):
        for srv in services:
            if srv.name in self._services:
                raise Exception(f'Service "{srv.name}" already registered')
            self._services[srv.name] = srv
            self.log.info(f'Service "{srv.name}" registered')

    def start(self):
        if self._task:
            raise Exception('Already started')
        self.log.info('START')
        self._task = asyncio.create_task(self._dispatch())

    def stop(self):
        if not self._task:
            return
        self.log.info('STOP')
        self._task.cancel()
        self._task = None

    @property
    def inbox(self) -> Queue[Message]:
        return self._inbox

    @property
    def outbox(self) -> Queue[ServiceResult]:
        return self._outbox

    async def _dispatch(self):
        def send_result(future: asyncio.Future[ServiceResult], context: contextvars.Context):
            self.log.info('SERVICE DONE')
            srv_res = future.result()
            self.log.info(f'    result: {srv_res}')
            self.log.info(f'    context: {context}')
            self.log.info(f'    context items: {context.items()}')
            self._outbox.put_nowait(srv_res)

        while True:
            msg = await self._inbox.get()
            self.log.info(f'Got new message: {msg}')
            try:
                service = self._services[msg.service]
            except KeyError:
                err_msg = f'Service "{msg.service}" not registered'
                self.log.error(err_msg)
                result = ServiceResult(mm_msg=msg, status=ServiceResultStatus.SERVICE_NOT_REGISTERED)
                self._outbox.put_nowait(result)
                continue

            srv_task = asyncio.create_task(service.exec(msg.text))
            srv_task.add_done_callback(send_result)
