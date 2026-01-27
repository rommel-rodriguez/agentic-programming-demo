from typing import Optional


class User:
    id: int
    name: str
    email: str

    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email


class Message:
    content: str


class Thread:
    user_id: int
    messages: list[Message]
