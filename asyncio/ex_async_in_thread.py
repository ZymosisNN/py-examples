import asyncio
import logging
import sys
import time
from threading import Thread


async def just_timer(n, event: asyncio.Event):
    await asyncio.sleep(1.5 * n)
    logging.getLogger(f'just_timer {n}').info('SET')
    event.set()


async def waiter(n):
    event = asyncio.Event()
    t = asyncio.create_task(just_timer(n, event))
    log = logging.getLogger(f'async waiter {n}')
    for i in range(10):
        log.info(f'{i} - {event.is_set()}')
        await asyncio.sleep(.4)

    await t


def func_with_async(n):
    asyncio.run(waiter(n))


def func_for_thread():
    log = logging.getLogger('sync waiter')
    for i in range(10):
        log.info(i)
        time.sleep(.3)


def main():
    t = Thread(target=func_with_async, args=(1,))
    t2 = Thread(target=func_with_async, args=(2,))
    t.start()
    t2.start()
    func_for_thread()
    t.join()
    logging.info('All done')


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')
    main()
