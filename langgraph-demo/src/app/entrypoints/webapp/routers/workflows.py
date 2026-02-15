import logging

from fastapi import APIRouter, Depends, HTTPException

from app.adapters.langgraph_agent import LangGraphAgent
from app.entrypoints.webapp.dependencies import get_query_agent_with_search
from app.entrypoints.webapp.models.workflows import LGQuery

logger = logging.getLogger(__name__)


router = APIRouter(tags=["agent-workflows"])


@router.get("/query-lgmodel", response_model=LGQuery)
async def query_lgmodel(
    query: str,
    thread_id: str,
    agent: LangGraphAgent = Depends(get_query_agent_with_search),
):
    logger.info("Langgraph endpoint reached")
    result = await agent(query, thread_id)

    logger.debug(f"Query output: {result}")
    if not result.get("result"):
        raise HTTPException(
            status_code=404, detail="The agent did not return a valid response"
        )
    return {"result": result["result"]}
