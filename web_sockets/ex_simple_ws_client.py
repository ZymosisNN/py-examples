import asyncio
import json

import websockets


async def hello():
    async with websockets.connect("ws://10.78.229.26:30005", subprotocols=["echo"], ping_timeout=None) as websocket:
        while True:
            mes = await websocket.recv()
            print('NEW MSG:')
            print(mes)
            data = json.loads(mes)
            if data['eventType'] == 'message':
                for i in data['data'].split('\n'):
                    print(i)


asyncio.run(hello())
