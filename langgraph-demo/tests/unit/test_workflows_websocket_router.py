from types import SimpleNamespace

import pytest
from fastapi import HTTPException, WebSocketDisconnect

from app.entrypoints.webapp.routers.workflows import chat_websocket, create_ws_ticket
from app.ports.agents import RunQueryResult
from app.ports.auth import AuthenticatedPrincipal


class FakeWebSocketTicketService:
    def __init__(self):
        self._tickets = {
            "valid-ticket": AuthenticatedPrincipal(user_id=1, tenant_id="tenant-1")
        }

    async def issue_for_access_token(self, access_token: str) -> str | None:
        if access_token != "valid-access-token":
            return None
        return "valid-ticket"

    async def consume(self, ticket: str) -> AuthenticatedPrincipal | None:
        return self._tickets.pop(ticket, None)


class FakeAgent:
    async def __call__(self, cmd, ctx=None) -> RunQueryResult:
        return RunQueryResult(result=f"reply:{cmd.thread_id}:{cmd.query}")


class FakeWebSocket:
    def __init__(self, ticket: str, messages: list[dict]):
        self.query_params = {"ticket": ticket}
        self.state = SimpleNamespace()
        self._messages = list(messages)
        self.sent_messages: list[dict] = []
        self.accepted = False

    async def accept(self) -> None:
        self.accepted = True

    async def receive_json(self) -> dict:
        if self._messages:
            return self._messages.pop(0)
        raise WebSocketDisconnect(code=1000)

    async def send_json(self, payload: dict) -> None:
        self.sent_messages.append(payload)


@pytest.mark.asyncio
async def test_create_ws_ticket_uses_bearer_token():
    response = await create_ws_ticket(
        authorization="Bearer valid-access-token",
        ticket_service=FakeWebSocketTicketService(),
    )

    assert response == {"ticket": "valid-ticket"}


@pytest.mark.asyncio
async def test_create_ws_ticket_rejects_invalid_bearer_token():
    with pytest.raises(HTTPException) as exc_info:
        await create_ws_ticket(
            authorization="Bearer invalid-access-token",
            ticket_service=FakeWebSocketTicketService(),
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_websocket_chat_consumes_ticket_and_runs_agent():
    websocket = FakeWebSocket(
        ticket="valid-ticket",
        messages=[
            {
                "type_": "chat.message",
                "thread_id": "thread-123",
                "message_id": "msg-123",
                "content": "hello",
            }
        ],
    )

    await chat_websocket(
        websocket,
        ticket_service=FakeWebSocketTicketService(),
        agent=FakeAgent(),
    )

    assert websocket.accepted is True
    assert websocket.state.user_id == 1
    assert websocket.state.tenant_id == "tenant-1"
    assert websocket.sent_messages == [
        {
            "type_": "chat.reply",
            "thread_id": "thread-123",
            "message_id": "msg-123",
            "content": "reply:thread-123:hello",
        }
    ]
