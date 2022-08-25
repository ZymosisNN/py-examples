import asyncio


async def check():
    print('check')
    await asyncio.sleep(.1)
    return True


class GenMaker:
    def __init__(self):
        self.gen = gen()

    def __aiter__(self):
        print('Making async generator')
        return self

    async def __anext__(self):
        await asyncio.sleep(.1)
        try:
            result = next(self.gen)
        except StopIteration:
            raise StopAsyncIteration

        return result


def gen():
    for i in range(4):
        yield i

    print('No more items')


async def main():
    result = [item async for item in GenMaker() if await check()]
    print(result)
    # async for i in GenMaker():
    #     print(i)


if __name__ == '__main__':
    asyncio.run(main())
