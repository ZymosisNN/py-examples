from typing import Literal

from pydantic import BaseModel

_cmds = Literal['lock', 'unlock']
_res_types = Literal[None, 'epc_node', 'enb_node']


class Host(BaseModel):
    ip: str
    username: str
    password: str


class RMReq(BaseModel):
    user: str
    cmd: _cmds
    res_type: _res_types = None
    res_id: int | None = None


class RMRsp(BaseModel):
    res_type: str
    res_id: int
    data: Host | list[Host]
