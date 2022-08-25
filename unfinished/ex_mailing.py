import asyncio
import aiosmtplib
import socket
import traceback
from email.message import EmailMessage

import loguru

LOG = loguru.logger


async def create_and_send_email(addr_from, addr_to, subject, msg_text):
    msg = EmailMessage()
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = subject
    msg.set_content(msg_text)

    LOG.info(f'FROM: {msg["From"]}')
    LOG.info(f'TO  : {msg["To"]}')
    LOG.info(f'MSG :\n{msg.as_string()}')

    try:
        await aiosmtplib.send(msg)
    except aiosmtplib.errors.SMTPException:
        LOG.error(traceback.format_exc())

    LOG.info('MAILING DONE')


async def main():
    test_addr_from = f'TestDialer@{socket.gethostname()}'
    test_addr_to = 'kgordeev@five9.com'
    test_subject = 'My sexy notification'
    test_text = 'Just some awesome message'

    asyncio.create_task(create_and_send_email(test_addr_from, test_addr_to, test_subject, test_text))

    for _ in range(10):
        LOG.info('ping')
        await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
