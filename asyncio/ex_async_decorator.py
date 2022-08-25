import asyncio


def decor(method):
    async def wrapped(self, *args, **kwargs):
        print(f'{self=}')
        try:
            return await method(self, *args, **kwargs)
        except asyncio.CancelledError:
            return 'CANCELLED'

    return wrapped


class A:
    @decor
    async def m(self, a, b):
        print(f'{self=}  {a=}  {b=}')
        await asyncio.sleep(2)
        return 'DONE'


async def f(coro):
    res = await asyncio.create_task(coro)
    print(res)
    return res


async def canceller(task):
    await asyncio.sleep(1)
    task.cancel()
    return 'canceller done'


async def main():
    obj = A()
    obj_coro = obj.m(1, b=2)
    t1 = asyncio.create_task(f(obj_coro))
    t2 = asyncio.create_task(canceller(t1))

    res = await asyncio.gather(t1, t2)
    print(f'{res=}')


if __name__ == '__main__':
    asyncio.run(main())
