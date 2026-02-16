from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeAlias, TypeVar

C = TypeVar("C", contravariant=True)
R = TypeVar("R", covariant=True)


# @dataclass(frozen=True, slots=True)
# class AgentQueryResult:
#     result: str


@dataclass(frozen=True, slots=True)
class AgentContext:
    trace_id: str | None = None
    media_refs: tuple[str, ...] = ()


# TODO: Find a proper place for agent commands and results classes
@dataclass(frozen=True, slots=True)
class RunQueryCommand:
    query: str
    thread_id: str


@dataclass(frozen=True, slots=True)
class RunQueryResult:
    result: str


class BaseAgent(Protocol, Generic[C, R]):
    async def __call__(self, cmd: C, ctx: AgentContext | None = None) -> R:
        """This must the the entrypointer for the agentic workflow"""
        ...


QueryAgent: TypeAlias = BaseAgent[RunQueryCommand, RunQueryResult]
