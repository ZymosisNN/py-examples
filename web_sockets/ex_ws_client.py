import argparse
import asyncio
import logging
import sys

import websockets


async def ws_client(uri: str):
    log = logging.getLogger('ws_client')

    log.info(f'Open WS to {uri}')
    async with websockets.connect(uri) as ws:
        log.info('Connected')

        data = 'preved medved'
        log.info(f'SEND "{data}"')
        await ws.send(data)

        log.info('Wait for data from server')
        data = await ws.recv()
        log.info(f'RECV: {data}')

        # Expect separate messages within 5 sec
        # try:
        #     while data := await asyncio.wait_for(ws.recv(), timeout=5):
        #         log.info(f'RECV: {data}')
        # except asyncio.TimeoutError:
        #     log.info('No more data from server')

    log.info('WS closed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', dest='ip', type=str, default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default=80)
    parser.add_argument('-e', dest='endpoint', type=str, default='')
    parser.add_argument('-v', dest='verbose', action='store_true')
    opts = parser.parse_args()

    logging.basicConfig(level=logging.NOTSET if opts.verbose else logging.INFO, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')

    asyncio.run(ws_client(f'ws://{opts.ip}:{opts.port}{opts.endpoint}'))
