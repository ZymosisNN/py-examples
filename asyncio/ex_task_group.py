import logging

import asyncio
from asyncio import TaskGroup
from log_tools import set_format


async def worker(delay: float, ex: Exception | None = None) -> float:
    log = logging.getLogger(f'worker({delay})')
    log.info('Begin')
    await asyncio.sleep(delay)
    if ex:
        raise ex
    log.info('End')
    return delay


async def main():
    log = logging.getLogger(f'MAIN')
    tasks: list[asyncio.Task] = []
    try:
        async with TaskGroup() as tg:
            for i in range(1, 5):
                log.info(f'Add worker({i})')
                if i == 2:
                    coro = worker(i, RuntimeError('HERE'))
                else:
                    coro = worker(i)
                tasks.append(tg.create_task(coro, name=str(i)))

            log.info('TaskGroup creation is done')

    except Exception as ex:
        log.error(f'Done with exception: {ex.__class__} {ex}')
        log.exception(ex)

    else:
        log.error('Done OK')

    for t in tasks:
        try:
            result = t.result()

        except Exception as ex:
            result = f'Got exception: {ex.__class__} {ex}'

        except asyncio.CancelledError:
            result = 'The task was cancelled'

        log.info(f'Task {t.get_name()}, result = {result}')


if __name__ == '__main__':
    set_format()
    asyncio.run(main())
