from fastapi import Depends, Request

from app.bootstrap.invoice_services import build_upload_attachment_use_case
from app.bootstrap.services import (
    build_query_agent_with_search,
    build_register_attachment_use_case,
)
from app.bootstrap.websocket_auth import (
    build_access_token_verifier,
    build_websocket_ticket_service,
    build_websocket_ticket_store,
)
from app.ports.agents import QueryAgent
from app.services.websocket_auth import WebSocketTicketService


def get_langgraph_db_pool(request: Request):
    return request.app.state.langgraph_pool


def get_session_factory(request: Request):
    return request.app.state.session_factory


def get_app_db_pool(request: Request):
    return request.app.state.app_pool


def get_checkpointer(request: Request):
    return request.app.state.checkpointer


def get_redis(request: Request):
    return request.app.state.redis


# TODO: Create a different DB Pool and replace the dependency with that pool
# in order other db operations not to use the same pool LangGraph is using
# which might have settings not apt for every use case.
def get_register_attachment_uc(session_factory=Depends(get_session_factory)):
    return build_register_attachment_use_case(session_factory)


def get_upload_attachment_uc(session_factory=Depends(get_session_factory)):
    return build_upload_attachment_use_case(session_factory=session_factory)


def get_query_agent_with_search(
    checkpointer=Depends(get_checkpointer),
) -> QueryAgent:
    return build_query_agent_with_search(checkpointer=checkpointer)


def get_websocket_ticket_service(
    redis=Depends(get_redis),
) -> WebSocketTicketService:
    ticket_store = build_websocket_ticket_store(redis)
    access_token_verifier = build_access_token_verifier()
    return build_websocket_ticket_service(
        ticket_store=ticket_store,
        access_token_verifier=access_token_verifier,
    )
