import random
import time
import threading
from queue import Queue

q = Queue()


class Worker(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        while True:
            t = self.q.get()
            print(f'{self.name} sleep {t}')
            time.sleep(t)
            print(f'    {self.name} sleep done')
            self.q.task_done()


for n in range(3):
    t = Worker(f'T{n}', q)
    t.setDaemon(True)
    t.start()

for n in range(10):
    q.put(random.randint(1, 7))

q.join()
