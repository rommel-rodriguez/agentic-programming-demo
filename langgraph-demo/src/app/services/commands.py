from dataclasses import dataclass
from uuid import UUID


class Command:
    pass


@dataclass(frozen=True)
class RunLGWorkflowCommand(Command):
    query: str


@dataclass(frozen=True, slots=True)
class UploadAttachmentContentCommand(Command):
    attachment_id: UUID
    content_type: str
    content: bytes
    original_filename: str | None = None
