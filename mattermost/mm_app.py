"""
MM slash proxy addr:
http://172.17.10.177:8081/v1/websocket

Authorization: Bearer 9qde3ddyEJqbFfoKHVqDTa6rFd2bu75OsSooOe9DNHcb4GMo
"""
import argparse
import asyncio
import logging
import sys

from mattermost.core import Dispatcher
# from mattermost.core import Dispatcher, MMProxyMsgReceiver, MMServiceResultSender
from mattermost.core.stubs import MMProxyMsgReceiverStub as MMProxyMsgReceiver, MMServiceResultSenderStub as MMServiceResultSender
from mattermost.services import ServiceTools

TOKEN = '9qde3ddyEJqbFfoKHVqDTa6rFd2bu75OsSooOe9DNHcb4GMo'  # TODO: hide


async def main(proxy_url: str, token: str):
    dispatcher = Dispatcher()
    msg_receiver = MMProxyMsgReceiver(url=proxy_url, token=token, inbox=dispatcher.inbox)
    result_sender = MMServiceResultSender(outbox=dispatcher.outbox)

    dispatcher.register_srv(
        ServiceTools('tools')
    )

    dispatcher.start()
    result_sender.start()
    msg_receiver.start()

    logging.info('eternal waiting')
    await asyncio.Future()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-addr', dest='addr', type=str, default='ws://172.17.10.177:8081/websocket/v1')
    parser.add_argument('-v', dest='verbose', action='store_true')
    opts = parser.parse_args()

    logging.basicConfig(level=logging.NOTSET if opts.verbose else logging.INFO, stream=sys.stdout,
                        format='%(asctime)-15s  |%(levelname)+8s| %(name)+30s |  %(message)s')

    asyncio.run(main(opts.addr, TOKEN))
