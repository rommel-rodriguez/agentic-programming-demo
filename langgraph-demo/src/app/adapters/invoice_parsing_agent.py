import json
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


class InvoiceAgentState(TypedDict):
    invoice_text: str
    invoice_json: str
    # invoice_image: bytes
    content: list[str]
    revision_number: int
    max_revisions: int


class InvoiceParsingAgent:
    def __init__(
        self,
        model,
        tools,
        checkpointer,
        thread_id: str,
        system: str = "",
    ):
        self.system = system
        self.model = model.bind_tools(tools)
        self.thread_id = thread_id
        graph_builder = StateGraph(InvoiceAgentState)
        graph_builder.add_node("llm", self.call_model)
        graph_builder.add_node("reflection", self.reflection)
        graph_builder.add_conditional_edges(
            "llm", self.is_valid_json, {True: END, False: "reflection"}
        )
        graph_builder.set_entry_point("llm")
        self.graph = graph_builder.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}

    def call_model(self, state: InvoiceAgentState):
        invoice_text = state["invoice_text"]

        messages = [
            HumanMessage(content=f"{invoice_text}"),
        ]
        if self.system:
            messages = [SystemMessage(content=self.system), *messages]  # type: ignore
        result = self.model.invoke(messages)
        logger.info(f"Called llm start node and got: {result}")
        if not result.content:
            logger.error(f"JSON string not returned by the LLM, response:\n{result}")
        invoice_json = result.content
        return {"revision_number": 1, "invoice_json": result.content}

    def reflection(self, state: InvoiceAgentState):
        # TODO: Need some kind of stopping condition here in order for it not to loop
        # forever by making use of max_revisions
        invoice_text = state["invoice_text"]
        invoice_json = state["invoice_json"]
        revision_number: int = state["revision_number"]
        max_revisions: int = state["max_revisions"]
        logger.info(
            f"Inside the reflection node, revision: {revision_number}"
            ", invoice_json: {invoice_json}"
        )
        # TODO: Needs a specialized system prompt to correct format mistakes in the JSON
        # string
        reflection_prompt = f"""You are an specialized agent that checks for errors in \
        what is supposed to be a valid JSON-formatted string, which came from an \
        invoice. The JSON format shows an error of some kind, and the desired output \
        is a correctly-JSON-formatted version of the JSON string. \
        As context you have the following: \
        invoice as text: \
        {invoice_text}
        invoice as JSON: \
        {invoice_json}
        IMPORTANT: Only return a valid JSON string, DO NOT return anything else.
        """
        # NOTE: Does this even work if there is not "human" message?
        messages = [SystemMessage(content=reflection_prompt)]
        ai_message = self.model.invoke(messages)
        invoice_json = ai_message.content
        return {"revision_number": revision_number + 1, "invoice_json": invoice_json}

    def is_valid_json(self, state: InvoiceAgentState):
        result = state["invoice_json"][-1]
        if not result:
            return False

        try:
            json.loads(result)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Raised while trying to parse json output {e}")
            return False
        return True

    def query_stream(self, invoice_text: str | None):
        thread = {"configurable": {"thread_id": self.thread_id}}

        for event in self.graph.stream({"invoice_text": invoice_text}, thread):
            for v in event.values():
                logger.info(
                    f"revison: {v['revision_number']}, json: {v['invoice_json']}"
                )

        return self.graph.get_state(thread)
