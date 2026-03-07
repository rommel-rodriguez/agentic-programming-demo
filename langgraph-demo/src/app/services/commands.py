from dataclasses import dataclass
from uuid import UUID

from app.domain.models import DocumentPurpose


class Command:
    pass


@dataclass(frozen=True)
class RunLGWorkflowCommand(Command):
    query: str


@dataclass(frozen=True, slots=True)
class RegisterAttachmentCommand(Command):
    user_id: int
    size_bytes: int
    content_type: str
    purpose: DocumentPurpose
    original_filename: str | None = None


@dataclass(frozen=True, slots=True)
class UploadAttachmentContentCommand(Command):
    attachment_id: UUID
    content_type: str
    content: bytes
    original_filename: str | None = None
