import asyncio
import websockets
import logging
import sys


async def ws_client():
    log = logging.getLogger('ws_client')
    # uri = "ws://10.11.150.210:80"
    # uri = "ws://192.168.10.1:80"
    uri = "ws://10.78.225.49:446"

    async with websockets.connect(uri, subprotocols=['echo'], ping_timeout=None) as ws:
        log.info('Connected')

        while True:
            data = await ws.recv()
            log.info(data.decode())

            # log.info('Sending shit...')
            # await ws.send('something')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+35s |  %(message)s')
    asyncio.run(ws_client())
