"""
# 1. добваляем генератор server() в задачи
# 2. в event_loop() поскольку есть задача, мы получаем read, server_socket = next(task)
#    в server()[т.е. task] мы вышли на первом yield и ждём следующего next
# 3. добавляем в словарь на мониторинг to_read[sock] = task[ждёт следующий next]
# 4. задачи закончились - переходим во внутренний while[пока что мониторим серверный сокет на чтение]
# 5. как только мы попытались установить соединение - отрабатывает selector,
#    добавляющий в задачи генератор, ждущий следующего next() tasks.append(to_read.pop(sock))
# 6. выходим из внутреннего while, поскольку появилась новая задача
# 7. делаем второй read, server_socket = next(task)
# 7.1 принимаем соединение и создаём клиентский сокет: client_socket, addr = server_socket.accept()
# 7.2 добавляем клиентский генератор в задачи: tasks.append(client(client_socket))
# 7.3 опять добавляем server_socket в словарь на мониторинг to_read[sock] = task[ждёт следующий next]
# 8. первая задача закончилась - переходим ко второй - обработка генератора client(client_socket)
# 8.1. read, client_socket = next(task2)
# 8.2. добавляем в мониторинг на чтение to_read[sock] = task2[ждёт следующего next]
# 8.3. задачи закончились - входим во внутренний цикл - мониторим два сокета на чтение
# 9. отправляем сообщение со стороны клиента
# 10. отрабатывает selector и добавляет генератор client() в задачи tasks
# 11. выходим из внутреннего while
# 12. write, client_socket = next(task2) - теперь уже на запись
# 13. добавляем в мониторинг на запись to_write[sock] = task2
# 13. поскольку буфер свободен то сразу работает selector и отдаст генератор в задачи
# 14. отправляем сообщение,
# 15. смещаемся до следующего yield и опять добавляем клиентский сокет в мониторинг на чтение
"""
import socket
from select import select

to_read = {}
to_write = {}
tasks = []


def server():
    print('    SRV: Start server')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('192.168.10.1', 60000))
    server_socket.listen()

    sockname = server_socket.getsockname()

    while True:
        print('    SRV: yield server socket')
        yield 'read', server_socket

        print(f'    SRV: accepting from {sockname}')
        client_socket, addr = server_socket.accept()

        print(f'    SRV: connection from {addr}')
        tasks.append(client(client_socket))


def client(sock):
    sockname = sock.getsockname()

    while True:
        print(f'    CLI: yield (read) {sockname}')
        yield 'read', sock

        print(f'    CLI: recv {sockname}')
        req = sock.recv(4096)

        print(f'    CLI recv result: "{str(req.decode()).strip()}"')
        if not req:
            break

        print(f'    CLI: yield (write) {sockname}')
        yield 'write', sock

        print(f'    CLI: send "OK" to {sockname}')
        sock.send('OK\n'.encode())

    print(f'    CLI: close {sockname}')
    sock.close()


def event_loop():
    while any((tasks, to_read, to_write)):

        while not tasks:
            print('select')
            ready_read, ready_write, _ = select(to_read, to_write, [])

            for sock in ready_read:
                print(f'add task (read): {sock.getsockname()}')
                tasks.append(to_read.pop(sock))

            for sock in ready_write:
                print(f'add task (write): {sock.getsockname()}')
                tasks.append(to_write.pop(sock))

        try:
            task = tasks.pop(0)

            print('next(task)')
            reason, sock = next(task)
            print(f'reason: {reason}, sock: {sock.getsockname()}')

            if reason == 'read':
                to_read[sock] = task
            if reason == 'write':
                to_write[sock] = task

        except StopIteration:
            print('DONE')


if __name__ == '__main__':
    tasks.append(server())
    event_loop()
