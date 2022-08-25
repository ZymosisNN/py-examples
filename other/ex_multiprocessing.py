from multiprocessing import Process, current_process, Queue
from time import sleep


DONE = 'DONE'


def producer(q):
    i = 0
    while i < 7:
        print(f'{current_process().name}: {i}')
        q.put(i)
        i += 1
        sleep(.5)

    q.put(DONE)


def consumer(q):
    while True:
        i = q.get()
        print(f'{current_process().name}: {i}')
        if i == DONE:
            break


if __name__ == '__main__':
    q = Queue()
    prod = Process(target=producer, name='Producer', args=(q,))
    cons = Process(target=consumer, name='Consumer', args=(q,))
    prod.start()
    cons.start()

    q.close()
    q.join_thread()

    prod.join()
    cons.join()
