from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch

from app.adapters.langgraph_agent import LangGraphAgent
from app.config import get_settings
from app.ports.agents import QueryAgent

# memory = SqliteSaver.from_conn_string(":memory:")
DEFAULT_SYSTEM_PROMPT = """You are a smart research assistant. Use the search engine to look up information. \
You are allowed to make multiple calls (either together or in sequence). \
Only look up information when you are sure of what you want. \
ATTENTION: If you need to look up some information before asking a follow up question, you are allowed to do that! \
you have access to tools the tavily search tool amongs them.
IMPORTANT: Make sure to review the tools available to you before making a judgement. \
Also, plan the order of tool calls and reasoning before all else.
"""
DEFAULT_MODEL_NAME = "gemini-2.5-flash"


def _build_default_tools() -> list:
    tools = []
    settings = get_settings()
    tavily_search = TavilySearch(max_results=2, tavily_api_key=settings.tavily_api_key)
    tools.append(tavily_search)
    return tools


def _build_default_model():
    settings = get_settings()
    model = ChatGoogleGenerativeAI(model=DEFAULT_MODEL_NAME)
    model.google_api_key = settings.gemini_api_key
    return model


# NOTE: Consider passing a model factory instead of a model directly
def build_query_agent_with_search(
    checkpointer,
    model=None,
    tools=None,
    system: str = DEFAULT_SYSTEM_PROMPT,
) -> QueryAgent:
    """
    Lazy by default:
    - if model/tools not provided, build them only when this function is called.
    - tests can inject fake model/tools.
    """
    model = model or _build_default_model()
    tools = tools or _build_default_tools()
    return LangGraphAgent(model, tools, checkpointer, system)
