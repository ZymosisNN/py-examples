from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol
from pydantic import BaseModel, Field, validator
from enum import StrEnum


class Message(BaseModel):
    channel_id: str = ''
    channel_name: str = ''
    service: str = Field('', alias='command')
    host: str = ''
    method: str = ''
    response_url: str = ''
    team_domain: str = ''
    team_id: str = ''
    text: str = ''
    token: str = ''
    trigger_id: str = ''
    url: str = ''
    user_id: str = ''
    user_name: str = ''

    @validator('service')
    def strip_slash(cls, v: str):
        return v.removeprefix('/')


class ServiceResultStatus(StrEnum):
    EXECUTED = 'Executed'
    FAILED = 'Failed'
    SERVICE_NOT_REGISTERED = 'Service not registered'


@dataclass
class ServiceResult:
    mm_msg: Message
    status: ServiceResultStatus
    result: str | None = None


class SlashService(Protocol):
    @abstractmethod
    async def exec(self, cmd: str) -> ServiceResult:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError
