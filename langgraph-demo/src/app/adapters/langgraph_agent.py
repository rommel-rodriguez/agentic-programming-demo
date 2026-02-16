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

from app.ports.agents import AgentContext, QueryAgent, RunQueryCommand, RunQueryResult

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class LangGraphAgent(QueryAgent):
    def __init__(self, model, tools, checkpointer, system: str = ""):
        self.system = system
        self.model = model.bind_tools(tools)
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
        return {"messages": [message]}

    def execute_action(self, state: AgentState):
        logger.debug("Inside the 'action' node")
        tool_calls = state["messages"][-1].tool_calls
        results = []
        for t in tool_calls:
            logger.info(f"Executing the {t['name']} tool")
            logger.debug(f"{t['name']} args: {t['args']}")
            result = self.tools[t["name"]].invoke(t["args"])
            results.append(
                ToolMessage(tool_call_id=t["id"], name=t["name"], content=str(result))
            )
        logger.info(f"Finished executing action/s. Going back to the model")
        return {"messages": results}

    def exists_action(self, state: AgentState):
        result = state["messages"][-1]
        return len(result.tool_calls) > 0

    # TODO: pass the thread_id as a parameter here
    def query_stream(self, input_query: str | None, thread_id: str):
        if not input_query:
            logger.error("The workflows must receive an initial instruction/message")
            raise ValueError(
                "The workflows must receive an initial instruction/message"
            )
        if not thread_id:
            logger.error("thread_id must have a value")
            raise ValueError("thread_id must have a value")

        messages = [HumanMessage(content=input_query)]
        thread = {"configurable": {"thread_id": thread_id}}

        for event in self.graph.stream({"messages": messages}, thread):
            for v in event.values():
                logger.info(v["messages"])

        return self.graph.get_state(thread)

    # TODO: pass the thread_id as a parameter here also
    # async def __call__(
    #     self, input_query: str, thread_id: str, stream=True, asynchronous=False
    # ) -> dict:
    async def __call__(
        self,
        cmd: RunQueryCommand,
        ctx: AgentContext | None = None,
        stream=True,
        asynchronous=False,
    ) -> RunQueryResult:
        if stream:
            if not asynchronous:
                agent_state = self.query_stream(cmd.query, cmd.thread_id)
                result = agent_state.values["messages"][-1].text
                return RunQueryResult(result=result)
            else:
                pass
        if not asynchronous:
            pass
        return RunQueryResult(result="")
