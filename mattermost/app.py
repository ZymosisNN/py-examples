import json
import logging
from asyncio.queues import Queue

from pydantic import ValidationError

from mattermost.datamodels import Message

"""
  channel_id = dejyhcuf578pxdqg3gyojg14mr
channel_name = 3qz7i4haatdb3phu85yhjiea5r__3qz7i4haatdb3phu85yhjiea5r
     command = /tools
        host = 172.17.10.176:55196
      method = POST
response_url = https://chat.yadro.com/hooks/commands/yaztfmifqi8d3np8mp8wa1fijr
 team_domain = yadro
     team_id = u5pkhemy7jbtuf4bf3bdoqnume
        text = 
       token = pg13bttictfxpfk8euk5cd5t6y
  trigger_id = M3JibW15ZGs5M3ljdGU3Z2RldTR0MzE1ZGg6M3F6N2k0aGFhdGRiM3BodTg1eWhqaWVhNXI6MTY3NDgzNDE2MjM1NTpNRVVDSUVOcmdDRmk2VklFK2N0MmkwZjVDS0lVTWlqazRIMnRHMlU5S3I2dkJhVHZBaUVBeUFkbGZRTzBuVGxVTUVOZU1BY25XVERQWWJyWHlVb1pyVkNwcHVXNzB3RT0=
         url = /command/tools/v1
     user_id = 3qz7i4haatdb3phu85yhjiea5r
   user_name = k.gordeev
"""


async def msg_receiver(queue: Queue):
    ws_client = None

    while True:
        msg_str = await ws_client.recv()
        data = json.loads(msg_str)
        try:
            msg = Message.parse_obj(data)
        except ValidationError as err:
            logging.error(f'Cannot parse received message: {err}')
        else:
            await queue.put(msg)


data = {"channel_id":"dejyhcuf578pxdqg3gyojg14mr","channel_name":"3qz7i4haatdb3phu85yhjiea5r__3qz7i4haatdb3phu85yhjiea5r","command":"/tools","host":"172.17.10.176:55196","method":"POST","response_url":"https://chat.yadro.com/hooks/commands/yaztfmifqi8d3np8mp8wa1fijr","team_domain":"yadro","team_id":"u5pkhemy7jbtuf4bf3bdoqnume","text":"","token":"pg13bttictfxpfk8euk5cd5t6y","trigger_id":"M3JibW15ZGs5M3ljdGU3Z2RldTR0MzE1ZGg6M3F6N2k0aGFhdGRiM3BodTg1eWhqaWVhNXI6MTY3NDgzNDE2MjM1NTpNRVVDSUVOcmdDRmk2VklFK2N0MmkwZjVDS0lVTWlqazRIMnRHMlU5S3I2dkJhVHZBaUVBeUFkbGZRTzBuVGxVTUVOZU1BY25XVERQWWJyWHlVb1pyVkNwcHVXNzB3RT0=","url":"/command/tools/v1","user_id":"3qz7i4haatdb3phu85yhjiea5r","user_name":"k.gordeev"}

m = Message.parse_obj(data)

print(m)





