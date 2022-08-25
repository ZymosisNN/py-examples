import socket
from select import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('192.168.10.1', 60000))
server_socket.listen()

to_monitor = []


def handle_client(sock):
    req = sock.recv(4096)
    if req:
        req = str(req.decode()).strip()
        print(f'recv: "{req}"')
        sock.send('OK\n'.encode())
    else:
        print('Connection closed')
        to_monitor.remove(sock)
        sock.close()


def handle_server(sock):
    client_socket, addr = sock.accept()
    print('Connection from', addr)
    to_monitor.append(client_socket)


def server_loop():
    while True:
        ready_read, _, _ = select(to_monitor, [], [])

        for sock in ready_read:
            if sock is server_socket:
                handle_server(sock)
            else:
                handle_client(sock)


if __name__ == '__main__':
    to_monitor.append(server_socket)
    server_loop()
