import asyncio
import time

urls = ['http://ya.ru', 'http://jopa.ru', 'http://rambler.ru', 'http://google.com']


async def delay(t):
    print(f'Sleep {t}')
    await asyncio.sleep(t)


def sync():
    for i in range(1, 4):
        print(f'Sleep {i}')
        time.sleep(i)


async def main():
    await asyncio.gather(*[delay(t) for t in range(1, 4)])


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(f'Done time: {time.time() - start:0.2f}')

    start = time.time()
    sync()
    print(f'Done time: {time.time() - start:0.2f}')

