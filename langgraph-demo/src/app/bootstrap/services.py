from app.adapters.langgraph_agent import LangGraphAgent


def langgraph_agent(model, tools, checkpointer, thread_id: str, system: str = ""):
    return LangGraphAgent(model, tools, checkpointer, thread_id, system)
