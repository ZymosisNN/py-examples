import time
import socket

from rm_msg_models import RMReq, RMRsp

with socket.create_connection(('127.0.0.1', 15555), timeout=10) as sock:
    req = RMReq(user='k.gordeev', res_type='epc_node', cmd='lock').json()
    print(f'Send {req}')
    sock.send(req.encode())

    print('Reading response')
    recv = sock.recv(1024)
    rsp = RMRsp.parse_raw(recv.decode())
    print(f'Received: {rsp}')
    res_id = rsp.res_id
    print(f'{res_id=}')

    print('Sleeping 2 sec...')
    time.sleep(2)

    req = RMReq(user='k.gordeev', cmd='unlock', res_id=res_id).json()
    sock.send(req)
