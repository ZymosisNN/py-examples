import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse

import stubs

APP = FastAPI()
LOG = logging.getLogger('views')


@APP.get('/node')
async def view_node(node_id: int):
    node = stubs.get_node_with_items(node_id)
    LOG.info(f'NODE: {node.node}')
    LOG.info(f'ITEMS: {node.items}')
    return JSONResponse(node.dict(by_alias=True))


@APP.get('/nodes')
async def view_nodes():
    nodes = stubs.get_nodes()
    LOG.info('NODES:')
    for i in nodes:
        LOG.info(i)
    return JSONResponse([n.dict() for n in nodes])
