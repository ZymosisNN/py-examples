import asyncio
import logging

import pytest

from mattermost.common import Message, ServiceResult, ServiceResultStatus
from mattermost.core import Dispatcher


NO_RESULT = ServiceResult(mm_msg=Message(), result='NO RESULT', status='JOPA')


@pytest.fixture
async def dispatcher():
    logging.debug('Make Dispatcher')
    dispatcher = Dispatcher()
    dispatcher.start()
    yield dispatcher
    dispatcher.stop()


@pytest.fixture
async def safe_result(dispatcher):
    logging.debug('Make result coro')
    timeout = 1

    async def coro() -> ServiceResult:
        try:
            return await asyncio.wait_for(dispatcher.outbox.get(), timeout=timeout)
        except asyncio.TimeoutError:
            logging.debug(f'Got no result in {timeout} seconds')
            return NO_RESULT

    return coro()


async def test_dispatcher1(dispatcher, safe_result):
    msg = Message(command='UnregisteredService')
    dispatcher.inbox.put_nowait(msg)

    result = await safe_result
    logging.debug(f'Result: {result}')
    assert result != NO_RESULT, 'No result from outbox queue'
