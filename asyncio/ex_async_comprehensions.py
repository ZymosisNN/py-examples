import asyncio


async def f1():
    await asyncio.sleep(.1)
    return 'f1'


async def f2():
    await asyncio.sleep(.1)
    return 'f2'


async def check():
    print('check')
    await asyncio.sleep(.1)
    return True


async def func_gen():
    for f in (f1, f2):
        yield f
        await asyncio.sleep(.1)


async def main():
    result = [await fun() for fun in (f1, f2)]
    print(result)
    result = [await fun() for fun in (f1, f2) if await check()]
    print(result)
    result = [await fun() async for fun in func_gen()]
    print(result)
    result = [await fun() async for fun in func_gen() if await check()]
    print(result)


if __name__ == '__main__':
    asyncio.run(main())
