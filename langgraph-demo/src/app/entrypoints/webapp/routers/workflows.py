import logging
from json import JSONDecodeError

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from pydantic import ValidationError

from app.entrypoints.webapp.dependencies import (
    get_query_agent_with_search,
    get_websocket_ticket_service,
)
from app.entrypoints.webapp.models.workflows import ChatIn, ChatOut, LGQuery, WSTicketOut
from app.ports.agents import QueryAgent, RunQueryCommand
from app.services.websocket_auth import WebSocketTicketService

logger = logging.getLogger(__name__)


router = APIRouter(tags=["agent-workflows"])


@router.get("/query-lgmodel", response_model=LGQuery)
async def query_lgmodel(
    query: str,
    thread_id: str,
    agent: QueryAgent = Depends(get_query_agent_with_search),
):
    logger.info("Langgraph endpoint reached")
    result = await agent(RunQueryCommand(query=query, thread_id=thread_id))

    logger.debug(f"Query output: {result}")
    if not result.result:
        raise HTTPException(
            status_code=404, detail="The agent did not return a valid response"
        )
    return {"result": result.result}


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    ticket_service: WebSocketTicketService = Depends(get_websocket_ticket_service),
    agent: QueryAgent = Depends(get_query_agent_with_search),
):
    ticket = websocket.query_params.get("ticket")
    if not ticket:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Missing ticket"
        )

    principal = await ticket_service.consume(ticket)
    if not principal:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Invalid ticket"
        )
    await websocket.accept()
    websocket.state.user_id = principal.user_id
    websocket.state.tenant_id = principal.tenant_id
    try:
        while True:
            try:
                raw = await websocket.receive_json()
            except JSONDecodeError as exc:
                logger.exception(f"malformed json string")
                await websocket.send_json(
                    {
                        "type_": "error",
                        "code": "malformed_json_string",
                        "detail": "failed to parse message as a JSON-formatted string",
                    }
                )
                continue

            logger.debug(f"received text: {raw}")
            try:
                msg = ChatIn.model_validate(raw)
            except ValidationError as exc:
                logger.debug(f"Invalid json input in chat:\n{raw}")
                await websocket.send_json(
                    {
                        "type_": "error",
                        "code": "invalid_json_message_shape",
                        "detail": exc.errors(),
                    }
                )
                continue
            reply = ChatOut(
                type_="chat.reply",
                thread_id=msg.thread_id,
                message_id=msg.message_id,
                content=(
                    await agent(
                        RunQueryCommand(query=msg.content, thread_id=msg.thread_id)
                    )
                ).result,
            )
            await websocket.send_json(reply.model_dump())
    except WebSocketDisconnect:
        logger.exception(f"client disconnected")


@router.post("/ws-ticket", response_model=WSTicketOut)
async def create_ws_ticket(
    authorization: str | None = Header(default=None),
    ticket_service: WebSocketTicketService = Depends(get_websocket_ticket_service),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    access_token = authorization.removeprefix("Bearer ").strip()
    ticket = await ticket_service.issue_for_access_token(access_token)
    if not ticket:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return {"ticket": ticket}
