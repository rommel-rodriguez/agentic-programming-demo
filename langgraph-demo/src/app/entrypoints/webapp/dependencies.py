from fastapi import Depends, Request

from app.bootstrap.services import build_query_agent_with_search
from app.ports.agents import BaseAgent


def get_checkpointer(request: Request):
    return request.app.state.checkpointer


def get_query_agent_with_search(
    checkpointer=Depends(get_checkpointer),
) -> BaseAgent:
    return build_query_agent_with_search(checkpointer=checkpointer)
