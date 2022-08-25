import asyncio
import websockets
import logging
import sys


async def ws_client():
    log = logging.getLogger('ws_client')
    # uri = "ws://10.11.150.210:80"
    uri = "ws://192.168.10.1:80"

    async with websockets.connect(uri) as ws:
        log.info('Connected')
        data = await ws.recv()
        log.info(f'{data=}')

        log.info('Sending shit...')
        await asyncio.sleep(1)
        await ws.send('something')

        log.info('Sending start...')
        await asyncio.sleep(1)
        await ws.send('start')

        log.info('Sleeping 5 sec...')
        await asyncio.sleep(5)

        log.info('Receiving...')
        while data := await asyncio.wait_for(ws.recv(), timeout=10):
            log.info(f'Received: {data}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')
    asyncio.run(ws_client())
