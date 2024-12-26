import logging

from fastapi import Request

from models import RequestRecord, Answer, EP
from ya_logging import get_logger

LOG = get_logger("storage")

recv_requests: list[RequestRecord] = []
endpoints: dict[str, Answer] = {}


async def save_request(req: Request) -> RequestRecord:
    path = req.scope['raw_path'].decode('utf-8')
    headers = dict(req.headers)
    body = (await req.body()).decode('utf-8')

    LOG.info('--- New request ---')
    LOG.info(f'Method: {req.method}')
    LOG.info(f'Path: {path}')
    LOG.log_dict(headers, description='Headers:', level=logging.INFO)
    LOG.trace(f'Body:\n{body}')

    record = RequestRecord(METHOD=req.method, PATH=path, HEADERS=headers, BODY=body)
    recv_requests.append(record)
    return record

def get_requests() -> list[RequestRecord]:
    return recv_requests

def set_answer(answer: Answer) -> None:
    endpoints[answer.ep_key] = answer


def get_answer(ep: EP) -> Answer:
    return endpoints[ep.ep_key]
