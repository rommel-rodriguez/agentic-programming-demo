import logging
from pathlib import Path

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.sqlite import SqliteSaver

from app.adapters.langgraph_agent import LangGraphAgent
from app.config import settings

# from app import bootstrap, config
from app.entrypoints import webapp

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


# import anyio


# from fastapi import FastAPI, File, HTTPException, UploadFile, status


app = webapp.fapi_app

UPLOAD_ROOT = Path("uploads")
CHUNK_SIZE = 1 * 1024 * 1024  # 1 MiB

d1 = {"key1": 12, "key2": "Aufwiedersehen"}

logger = logging.getLogger(__name__)


@app.get("/test-string")
def test_endpoint():
    logger.info("test-string endpoint aufwiedersehen")
    return "Hallo FastAPI world!"


@app.get("/test-dict")
def test_dictionary():
    logger.error("test-dict endpoint triggered")
    return d1


@app.get("/test-debug")
def test_debug():
    logger.debug("Is this printed while in INFO logger level?")
    return d1


@app.get("/test-warning")
def test_warning():
    logger.warning("Is this Warning logged at INFO level logger?")
    return d1


@app.get("/test-exception")
def test_exception():
    def divide(a, b):
        try:
            result = a / b
        except ZeroDivisionError:
            logger.exception("Hey Ho!")
        except TypeError:
            logger.exception("hey TE!")
        else:
            return result

    result = divide(1, 0)
    return result


@app.get("/query-lgmodel")
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
