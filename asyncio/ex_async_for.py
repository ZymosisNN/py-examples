import asyncio


async def ticker(delay, to):
    for i in range(to):
        yield i, delay
        await asyncio.sleep(delay)


async def run(k):
    async for i in ticker(k, 10):
        print(i)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(asyncio.gather(run(1), run(2)))
finally:
    loop.close()

