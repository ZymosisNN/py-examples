import asyncio
import sys
import logging
from functools import partial


logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)-15s  | %(name)+20s |  %(message)s')


def cb(task, *, name):
    log = logging.getLogger(name)
    log.info(f'    task: {task}')
    try:
        log.info(task.result())
    except asyncio.CancelledError:
        log.info('    CANCELLED')


async def coro(name):
    log = logging.getLogger(name)
    log.info('Begin')
    await asyncio.sleep(2)
    log.info('End')
    return 'OK'


async def main():
    log = logging.getLogger('main')

    t1 = asyncio.create_task(coro('coro -'))
    t1.add_done_callback(partial(cb, name='<cb> coro -'))

    t2 = asyncio.create_task(coro('coro +'))
    t2.add_done_callback(partial(cb, name='<cb> coro +'))

    log.info('Before sleep')
    await asyncio.sleep(1)
    log.info('After sleep')

    t1.cancel()

    try:
        res = await t1
    except asyncio.CancelledError:
        log.info('t1 CANCELLED')
        res = 'NOK'
    log.info(f'res: {res}')

    try:
        res = await t2
    except asyncio.CancelledError:
        log.info('t2 CANCELLED')
        res = 'NOK'
    log.info(f'res: {res}')


if __name__ == '__main__':
    asyncio.run(main())
