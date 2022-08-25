import logging.handlers
import socket

fmt = '[%(levelname)-8s] %(message)s'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(format=fmt)

# handler = logging.handlers.SysLogHandler(address=('10.26.5.24', 515))
handler = logging.handlers.SysLogHandler(address=('192.168.10.2', 514), socktype=socket.SOCK_STREAM)
log.addHandler(handler)

log.warning('='*100)
log.warning('Hello world!')
log.warning('='*100)
