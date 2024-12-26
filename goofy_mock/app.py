from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_400_BAD_REQUEST

from ya_logging import get_logger
import storage
from models import Answer

app = FastAPI()
LOG = get_logger("mock")


@app.get("/REQUESTS", status_code=HTTP_200_OK)
async def get_received_requests() -> JSONResponse:
    return JSONResponse(content=[rec.model_dump() for rec in storage.get_requests()])


@app.post('/SET-RSP', status_code=HTTP_202_ACCEPTED)
async def mgmt_handler(answer: Answer):
    LOG.info(answer)
    return Response(f'Mock response is set for {answer.ep_key}')


@app.api_route("/{path:path}", methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
async def handle_item(req: Request) -> Response:
    record = await storage.save_request(req)
    try:
        answer = storage.get_answer(record)
    except KeyError as e:
        raise HTTPException(HTTP_400_BAD_REQUEST, f'Mock answer is not set for {record.ep_key}')

    if isinstance(answer.BODY, dict):
        return JSONResponse(content=answer.BODY, status_code=answer.STATUS, headers=answer.HEADERS)
    else:
        return Response(content=answer.BODY, status_code=answer.STATUS, headers=answer.HEADERS)
