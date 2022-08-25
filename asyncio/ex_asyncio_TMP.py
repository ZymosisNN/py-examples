import asyncio


async def worker(name, have_ex=False):
    print(f'{name} - start')
    for i in range(10):
        await asyncio.sleep(0.1)
        print(f'{name} - {i}')

        if i == 3 and have_ex:
            raise RuntimeError(f'{name} - mne pizda!')


async def master(m_idx):
    tasks = []
    for name in [f'master({m_idx}) - worker #{i}' for i in range(4)]:
        tasks.append(asyncio.create_task(worker(name, m_idx == 0)))
        await asyncio.sleep(0.1)

    done, pending = await asyncio.wait(tasks)
    print(f'master({m_idx}) done:')
    for t in done:
        print(t)
        print(t.result())
    print(f'master({m_idx}) pending:')
    for t in pending:
        print(t)


async def main():
    tasks = []
    for name in range(2):
        tasks.append(asyncio.create_task(master(name)))
        await asyncio.sleep(0.1)

    # res = await asyncio.gather(*tasks)
    # print(f'main res: {res}')

    done, _ = await asyncio.wait(tasks)
    print('FINAL:')
    for t in done:
        print(t)
        print(t.result())


if __name__ == '__main__':
    asyncio.run(main())
