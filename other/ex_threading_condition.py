import logging
import threading
from time import sleep

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s (%(threadName)-9s) %(message)s')

cv = threading.Condition()


def t(name, cv):
    logging.debug('{}: Started'.format(name))
    with cv:
        logging.debug('{}:    Wait IN'.format(name))
        cv.wait()
        logging.debug('{}:    Wait OUT'.format(name))
    sleep(1)
    logging.debug('{}:    Out'.format(name))


def p(name, cv):
    logging.debug('{}: Started'.format(name))
    sleep(1)
    with cv:
        logging.debug('{}: notifyAll IN'.format(name))
        cv.notifyAll()
        logging.debug('{}: notifyAll OUT'.format(name))
    sleep(2)
    logging.debug('{}: Out'.format(name))


threading.Thread(target=t, args=('T1', cv)).start()
threading.Thread(target=t, args=('T2', cv)).start()
threading.Thread(target=p, args=('P1', cv)).start()


