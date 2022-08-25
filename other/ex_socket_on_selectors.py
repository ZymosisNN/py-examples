import socket
import selectors

selector = selectors.DefaultSelector()


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('192.168.10.1', 60000))
    server_socket.listen()

    selector.register(fileobj=server_socket, events=selectors.EVENT_READ, data=handle_server)


def handle_server(sock):
    client_socket, addr = sock.accept()
    print('Connection from', addr)
    selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=handle_client)


def handle_client(sock):
    req = sock.recv(4096)
    if req:
        req = str(req.decode()).strip()
        print(f'recv: "{req}"')
        sock.send('OK\n'.encode())
    else:
        print('Connection closed')
        selector.unregister(sock)
        sock.close()


def server_loop():
    while True:
        events = selector.select()
        for event, _ in events:
            print('Event from', event.fileobj.getsockname())
            cb = event.data
            cb(event.fileobj)


if __name__ == '__main__':
    server()
    server_loop()
