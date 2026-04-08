from typing import Literal

from pydantic import BaseModel


class LGQuery(BaseModel):
    result: str


class WSTicketOut(BaseModel):
    ticket: str


class ChatIn(BaseModel):
    type_: Literal["chat.message"]
    thread_id: str
    message_id: str
    content: str


class ChatOut(BaseModel):
    type_: Literal["chat.reply"]
    thread_id: str
    message_id: str
    content: str
