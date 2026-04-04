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

from app.entrypoints.webapp.dependencies import get_query_agent_with_search
from app.entrypoints.webapp.models.workflows import ChatIn, ChatOut, LGQuery
from app.ports.agents import QueryAgent, RunQueryCommand

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
async def chat_websocket(websocket: WebSocket):
    ticket = websocket.query_params.get("ticket")
    if not ticket:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason="Missing ticket"
        )

    principal = verify_ws_ticket(ticket)
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
                content=f"Echo:\n{msg}",
            )
            await websocket.send_json(reply.model_dump())
    except WebSocketDisconnect:
        logger.exception(f"client disconnected")


@router.post("/wf/ws-ticket")
async def create_ws_ticket(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    access_token = authorization.removeprefix("Bearer ").strip()
    user = verify_access_token(access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    ticket = mint_ws_ticket(
        sub=user.user_id,
        ttl_seconds=30,
        single_use=True,
    )
    return {"ticket": ticket}
