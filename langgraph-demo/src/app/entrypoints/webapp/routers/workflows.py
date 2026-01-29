from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver

from app.adapters.langgraph_agent import LangGraphAgent
from app.config import settings  # type:ignore
from app.entrypoints.webapp.models.workflows import LGQuery

tool = TavilySearch(max_results=2, tavily_api_key=settings.tavily_api_key)
# memory = SqliteSaver.from_conn_string(":memory:")
prompt = """You are a smart research assistant. Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
ATTENTION: If you need to look up some information before asking a follow up question, you are allowed to do that! \
you have access to tools the tavily search tool amongs them.
IMPORTANT: Make sure to review the tools available to you before making a judgement. \
Also, plan the order of tool calls and reasoning before all else.
"""
MODEL = "gemini-2.5-flash"
model = ChatGoogleGenerativeAI(model=MODEL)
model.google_api_key = settings.gemini_api_key
messages = [HumanMessage(content="What is the weather in San Francisco?")]


router = APIRouter()


@router.get("/query-lgmodel", response_model=LGQuery)
async def query_lgmodel(query: str):
    agent_state = None
    with SqliteSaver.from_conn_string(":memory:") as memory:
        abot = LangGraphAgent(
            model, [tool], thread_id="3", system=prompt, checkpointer=memory
        )
        agent_state = abot.query_stream(query)

    result = agent_state.values["messages"][-1].text
    if not result:
        pass  # NOTE: Raise/return some error here.
    return {"result": result}
