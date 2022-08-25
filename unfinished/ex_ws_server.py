import asyncio
import websockets
import logging
import sys


async def handler_inner_task():
    while True:
        await asyncio.sleep(1)


async def ws_handler(ws, path):
    log = logging.getLogger('ws_handler')
    log.debug(f'WS  : {ws}')
    log.debug(f'path: {path}')

    log.info('Receiving...')
    # data = await ws.recv()
    # log.info(f'Received: {data}')

    async for message in ws:
        log.debug(f'message: {message}')

    log.info('Sending...')
    await ws.send('server message 1')
    await ws.send('server message 2')


async def ws_server():
    log = logging.getLogger('ws_server')
    host = '10.11.150.210'

    # asyncio.create_task(websockets.serve(ws_handler, host, 80))
    await websockets.serve(ws_handler, host, 80)

if __name__ == '__main__':
    host = '10.11.150.210'
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')
    # asyncio.run(ws_server())
    # asyncio.get_event_loop().run_until_complete(websockets.serve(ws_handler, host, 80))
    # asyncio.get_event_loop().run_forever()
