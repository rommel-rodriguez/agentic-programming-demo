import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph

MODEL = "gemini-2.5-flash"


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class LangGraphAgent:
    def __init__(self, model, tools, checkpointer, system: str = ""):
        self.system = system
        # self.model = model.bind_tools(tools)  ## NOTE: Different for Gemini
