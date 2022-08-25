import logging
import os
from functools import partial


fmt = '%(asctime)-15s [%(levelname)-8s] %(procType)-6s %(processName)s %(process)d %(threadName)-10s %(name)-34s | %(message)s'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(format=fmt)

var = 'jopa'

pid = os.fork()
if pid:
    proc_type = {'procType': 'PARENT'}
    var = 'Parent'
else:
    proc_type = {'procType': 'CHILD'}
    var = 'Child'

log.info = partial(log.info, extra=proc_type)
log.info(f'var = {var}')
