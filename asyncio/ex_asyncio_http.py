import logging
import sys
import asyncio
import aiohttp
from time import perf_counter


def save_data(data, fname):
    with open(fname, 'wb') as file:
        file.write(data)


async def write_file(session, url):
    async with session.get(url) as response:
        data = await response.read()
        fname = f"_file-{str(response.url).split('/')[-1]}"
        save_data(data, fname)


async def main():
    url = 'https://loremflickr.com/320/240'
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(4):
            tasks.append(asyncio.create_task(write_file(session, url)))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')
    start = perf_counter()
    asyncio.run(main())
    print(perf_counter() - start)
