from app.ports.agents import BaseAgent

from .commands import RunLGWorkflowCommand


class RunLGWorkflow:
    def __init__(
        self,
        checkpointer,  # NOTE: Or some kind of persistence technology
        agent: BaseAgent,
    ):
        pass

    def __call__(self, cmd: RunLGWorkflowCommand):
        pass
