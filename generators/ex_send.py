import asyncio


def gen():
    for i in range(5):
        recv = yield
        print(f'{recv=}')

    print('gen DONE')
    return 'result'


# g = gen()
# print('first', next(g))
#
# for n in range(100, 110):
#     print(g.send(n))


async def main():
    t = asyncio.create_task(gen())
    res = await t
    print(res)


if __name__ == '__main__':
    asyncio.run(main())

