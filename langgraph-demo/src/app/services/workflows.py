from .commands import RunLGWorkflowCommand


class RunLGWorkflow:
    def __init__(
        self,
        checkpointer,  # NOTE: Or some kind of persistence technology
    ):
        pass

    def __call__(self, cmd: RunLGWorkflowCommand):
        pass
