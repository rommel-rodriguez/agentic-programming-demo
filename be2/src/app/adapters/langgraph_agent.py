import logging
import operator
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class LangGraphAgent:
    def __init__(self, model, tools, checkpointer, system: str = ""):
        self.system = system
        self.model = model.bind_tools(tools)  ## NOTE: Different for Gemini
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("llm", self.call_model)
        graph_builder.add_conditional_edges(
            "llm", self.exists_action, {True: "action", False: END}
        )
        graph_builder.add_node("action", self.execute_action)
        graph_builder.add_edge("action", "llm")
        graph_builder.set_entry_point("llm")
        self.graph = graph_builder.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}

    def call_model(self, state: AgentState):
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        return {"messages": message}

    def execute_action(self, state: AgentState):
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for t in tool_calls:
            logger.info(f"Calling {t}")
            result = self.tools[t["name"]].invoke(t["args"])
            results.append(
                ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result))
            )
        logger.info(f"Finished executing action/s. Going back to the model")
        return {"messages": results}

    def exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(result.tool_calls) > 0


if __name__ == "__main__":
    from langchain_google_genai import ChatGoogleGenerativeAI

    model = ChatGoogleGenerativeAI(model=MODEL)
