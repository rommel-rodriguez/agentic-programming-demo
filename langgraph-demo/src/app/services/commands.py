from dataclasses import dataclass


class Command:
    pass


@dataclass(frozen=True)
class RunLGWorkflowCommand(Command):
    query: str
