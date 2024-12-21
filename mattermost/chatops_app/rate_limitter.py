import queue
import threading
import logging
from time import time, sleep

from chatops_app.abstracts import LogMixin

__all__ = ['RateLimiter']


class RateLimiterNotFound(Exception):
    pass


class RateLimiterMeta(type):
    # _limiters: dict[str, 'RateLimiter'] = {}  # TODO: uncomment when Python 3.10
    _limiters: dict = {}

    def __call__(cls, name: str, interval: float = None):
        if name not in cls._limiters:
            if not interval:
                raise RateLimiterNotFound(
                    f'RateLimiter "{name}" must be created firstly (call once with defined parameter "interval")')
            cls._limiters[name] = super().__call__(name=name, interval=interval)

        return cls._limiters[name]

    @classmethod
    def remove(mcs, limiter_to_del) -> None:
    # def remove(mcs, limiter_to_del: 'RateLimiter') -> None:  # TODO: uncomment when Python 3.10
        for name, limiter in mcs._limiters.items():
            if limiter == limiter_to_del:
                mcs._limiters.pop(name)
                return


class RateLimiter(LogMixin, metaclass=RateLimiterMeta):
    def __init__(self, *, name: str = None, interval: float = None):
        super().__init__(name)
        self._stop_signal = False
        self._interval = interval
        self._requests_queue: queue.Queue[threading.Event] = queue.Queue()
        self._consumer_thread = threading.Thread(target=self._queue_handler, name='rate-limit-queue')
        self._rlock = threading.RLock()
        self._consumer_thread.start()
        self._log.info(f'RateLimiter thread started (interval: {interval} sec)')

    def _queue_handler(self):
        last_time = 0
        while not self._requests_queue.empty() or not self._stop_signal:
            event = self._requests_queue.get()
            self._requests_queue.task_done()

            past_time = time() - last_time
            if past_time < self._interval:
                wait_time = self._interval - past_time
                self.trace(f'Rate limiting: wait {wait_time:.3f} sec...')
                sleep(wait_time)

            last_time = time()
            event.set()

    def __call__(self, destroy=False) -> None:
        with self._rlock:
            if destroy:
                self._log.debug('Stopping rate limiting')
                self._stop_signal = True
                self._requests_queue.join()
                self._log.debug('Queue finished')
                self._consumer_thread.join()
                self._log.debug('Queue consumer thread finished')
                RateLimiterMeta.remove(self)
                return

        if self._stop_signal:
            self._log.warning('No rate limits')
            return

        event = threading.Event()
        self._requests_queue.put_nowait(event)
        event.wait()

    def __del__(self):
        self._log.info('DELETED')

    @classmethod
    def use(cls, name: str):
        def decor(func):
            def wrap(*args, **kwargs):
                cls(name=name)()
                func(*args, **kwargs)
            return wrap

        return decor


__limiter_name = 'TEST'


@RateLimiter.use(__limiter_name)
def _test_worker(name):
    logging.getLogger(f'worker-{name}').info('Done')


def _test():
    limiter = RateLimiter(name=__limiter_name, interval=.4)
    ths = [threading.Thread(target=_test_worker, args=(i,),  name=f'worker-thread-{i}') for i in range(10)]
    for t in ths:
        logging.info(f'Start {t.name}')
        t.start()

    sleep(2)
    logging.info('STOP LIMITER')
    limiter(destroy=True)

    new_ths = [threading.Thread(target=_test_worker, args=(i,), name=f'worker-thread-{i}') for i in range(10, 20)]
    for t in new_ths:
        logging.info(f'Start {t.name}')
        t.start()
    ths.extend(new_ths)

    for t in ths:
        t.join()


if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.NOTSET, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(threadName)20s | %(name)+30s |  %(message)s')
    _test()
