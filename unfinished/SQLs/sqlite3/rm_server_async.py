import asyncio

from rm_msg_models import RMRsp, RMReq, Host


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    data = await reader.read(1024)
    req = RMReq.parse_raw(data.decode())
    print(f"Received {req} from {addr}")

    rsp = RMRsp(res_type=req.res_type, data=Host(ip='123', username='aaa', password='bbb')).json()
    print(f'Send: {rsp}')
    writer.write(rsp.encode())
    await writer.drain()

    print('Close the connection')
    writer.close()


async def run_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 15555)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(run_server())
