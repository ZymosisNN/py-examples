import threading
import time

ev = threading.Event()


def T(ev):
    print('Wating event')
    ev.wait(10)
    print('Finished')


t = threading.Thread(target=T, args=[ev])
t.start()

time.sleep(2)

ev.set()

t.join()
