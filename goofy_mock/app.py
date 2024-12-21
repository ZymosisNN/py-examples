import logging
from typing import Annotated, Any

from fastapi import Request, FastAPI, Body, Header
from fastapi.responses import JSONResponse
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED

from ya_logging import get_logger

app = FastAPI()
LOG = get_logger("yati.relay")

received_requests = []


@app.get("/REQUESTS", status_code=HTTP_200_OK)
async def handle_item() -> JSONResponse:
    return JSONResponse(content=received_requests)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], status_code=HTTP_200_OK)
async def handle_item(req: Request) -> Response:
    path = req.scope['raw_path'].decode('utf-8')
    headers = dict(req.headers)
    body = (await req.body()).decode('utf-8')

    LOG.info('--- New request ---')
    LOG.info(f'Method: {req.method}')
    LOG.info(f'Path: {path}')
    LOG.log_dict(headers, description='Headers:', level=logging.INFO)
    LOG.trace(f'Body:\n{body}')

    received_requests.append({
        'METHOD': req.method,
        'PATH': path,
        'HEADERS': headers,
        'BODY': body,
    })

    return Response(status_code=HTTP_202_ACCEPTED)
