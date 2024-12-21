import argparse
import asyncio
import json
import logging
import sys

import websockets


async def ws_handler(ws, path: str):
    log = logging.getLogger(f'client {ws.remote_address}')
    log.info(f'WS: {ws}')
    log.info(f'Path: {path}')

    for i in range(6):
        data = json.dumps({'type': 'MSG', 'data': f'epc message #{i}'})
        log.info(f'SEND: {data}')
        try:
            await ws.send(data)
        except websockets.ConnectionClosed:
            break

        await asyncio.sleep(2)

    log.info('DONE')


async def ws_server(host: str, port: int):
    async with websockets.serve(ws_handler, host, port):
        await asyncio.Future()  # To run forever


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', dest='ip', type=str, default='127.0.0.1')
    parser.add_argument('-p', dest='port', type=int, default=446)
    parser.add_argument('-v', dest='verbose', action='store_true')
    opts = parser.parse_args()

    logging.basicConfig(level=logging.NOTSET if opts.verbose else logging.INFO, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')

    asyncio.run(ws_server(opts.ip, opts.port))
