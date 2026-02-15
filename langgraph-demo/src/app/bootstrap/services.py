from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from app.adapters.langgraph_agent import LangGraphAgent
from app.config import settings  # type:ignore

tool = TavilySearch(max_results=2, tavily_api_key=settings.tavily_api_key)
tools = [tool]
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
gemini_model = ChatGoogleGenerativeAI(model=MODEL)
gemini_model.google_api_key = settings.gemini_api_key


# NOTE: Consider passing a model factory instead of a model directly
def build_query_agent_with_search(
    checkpointer,
    model=gemini_model,
    tools=tools,
    system: str = prompt,
):
    return LangGraphAgent(model, tools, checkpointer, system)
