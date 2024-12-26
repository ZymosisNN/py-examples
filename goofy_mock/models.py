from typing import Any

from pydantic import BaseModel


class EP(BaseModel):
    METHOD: str
    PATH: str

    @property
    def ep_key(self):
        return f'[{self.METHOD}] {self.PATH}'


class RequestRecord(EP):
    HEADERS: dict
    BODY: Any


class Answer(EP):
    STATUS: int
    BODY: Any
    HEADERS: dict
