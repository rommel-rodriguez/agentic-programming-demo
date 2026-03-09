from fastapi import Depends, Request

from app.bootstrap.services import build_query_agent_with_search
from app.ports.agents import QueryAgent


def get_langgraph_db_pool(request: Request):
    return request.app.state.langgraph_pool


def get_app_db_pool(request: Request):
    return request.app.state.app_pool


def get_checkpointer(request: Request):
    return request.app.state.checkpointer


# TODO: Create a different DB Pool and replace the dependency with that pool
# in order other db operations not to use the same pool LangGraph is using
# which might have settings not apt for every use case.
def get_register_attachmetn_uc(app_pool=Depends(get_app_db_pool)):
    return app_pool


def get_query_agent_with_search(
    checkpointer=Depends(get_checkpointer),
) -> QueryAgent:
    return build_query_agent_with_search(checkpointer=checkpointer)
