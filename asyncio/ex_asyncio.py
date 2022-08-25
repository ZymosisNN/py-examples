import asyncio


async def worker():
    print('worker started')
    await asyncio.sleep(3)
    print('worker done')
    return 'worker result'


async def starter_awaiter():
    future = asyncio.ensure_future(worker())
    result = await future
    print(f'Result of worker: {result}')


async def starter_checker():
    future = asyncio.ensure_future(worker())
    while not future.done():
        print(f'Waiting for result...')
        await asyncio.sleep(1)
    print(f'Result of worker: {future.result()}')


async def starter_callbacker():
    done = []

    def cb(res):
        print(f'CB, result: {res}')
        done.append(res)

    future = asyncio.ensure_future(worker())
    future.add_done_callback(cb)

    while not done:
        print(f'Waiting for result...')
        await asyncio.sleep(1)

    print(f'Result of worker: {future.result()}')


async def starter_tasker():
    asyncio.create_task(worker())
    # asyncio.ensure_future(worker())
    for _ in range(4):
        print('Just doing something...')
        await asyncio.sleep(1)


if __name__ == '__main__':

    asyncio.run(starter_awaiter())
    print('-' * 100)
    asyncio.run(starter_checker())
    print('-' * 100)
    asyncio.run(starter_callbacker())
    print('-' * 100)
    asyncio.run(starter_tasker())

