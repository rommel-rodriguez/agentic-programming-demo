import logging
from json import JSONDecodeError

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
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
    await websocket.accept()
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
