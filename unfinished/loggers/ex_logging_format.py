import os
import threading
import logging
import sys


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

sh = logging.StreamHandler(stream=sys.stdout)
sh.setLevel(logging.DEBUG)

sherr = logging.StreamHandler(stream=sys.stderr)
sherr.setLevel(logging.WARNING)

fmt_patt = '%(asctime)-15s [%(levelname)-8s] %(processName)s %(process)d %(threadName)-10s %(name)-34s | %(message)s'
fmt = logging.Formatter(fmt_patt)

sh.setFormatter(fmt)
sherr.setFormatter(fmt)

log.addHandler(sh)
log.addHandler(sherr)


class MyThread(threading.Thread):
    def __init__(self, pipe, master=True):
        super().__init__()
        self.pipe = pipe
        self.master = master

    def run(self):
        if self.master:
            log.info(f'say preved to pipe {self.pipe}')
            print('preved', file=os.fdopen(self.pipe, 'w'))

        else:
            log.info(f'open pipe {self.pipe}')
            pipein = os.fdopen(self.pipe)
            log.info('read pipe')
            data = pipein.readlines()
            log.info(data)

        log.warning('DONE')


if __name__ == '__main__':
    r, w = os.pipe()
    m = MyThread(w)
    s = MyThread(r, master=False)
    m.start()
    s.start()
    m.join()
    s.join()
