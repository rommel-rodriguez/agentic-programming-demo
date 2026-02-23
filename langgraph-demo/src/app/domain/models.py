from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    id: int
    name: str
    email: str


@dataclass
class Message:
    content: str


@dataclass
class Thread:
    user_id: int
    messages: list[Message]


@dataclass
class Invoice:
    amount: float
    currency: str
    emission_date: date
    due_date: date
    hash: bytes
