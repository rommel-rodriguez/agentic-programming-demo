from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class User:
    id: int
    name: str
    email: str


@dataclass
class Message:
    content: str
    type: str


@dataclass
class Thread:
    user_id: int
    messages: list[Message]


@dataclass
class Invoice:
    user: User
    amount: float
    currency: str
    due_date: date
    emission_date: date


class DocumentStatus(StrEnum):
    PENDING_UPLOAD = "pending_upload"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentPurpose(StrEnum):
    RESUME = "resume"
    INVOICE = "invoice"
    CONTEXT = "context"


@dataclass(frozen=True, slots=True, kw_only=True)
class Document:
    user_id: int
    filename: str
    content_type: str
    size_bytes: int
    purpose: DocumentPurpose

    id: UUID = field(default_factory=uuid4)
    status: DocumentStatus = DocumentStatus.PENDING_UPLOAD
    storage_key: str | None = None
    checksum_sha256: str | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    uploaded_at: datetime | None = None
    processed_at: datetime | None = None

    chunk_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("filename cannot be empty")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must be >= 0")
        if "/" not in self.content_type:
            raise ValueError("content_type must be a valid MIME type")

    def mark_uploaded(
        self,
        *,
        storage_key: str,
        checksum_sha256: str,
        uploaded_at: datetime | None = None
    ) -> "Document":
        if self.status != DocumentStatus.PENDING_UPLOAD:
            raise ValueError("document must be pending upload before completion")
        return replace(
            self,
            status=DocumentStatus.UPLOADED,
            storage_key=storage_key,
            checksum_sha256=checksum_sha256,
            uploaded_at=uploaded_at or datetime.now(timezone.utc),
        )

    def mark_ready(self, *, chunk_count: int) -> "Document":
        if self.status not in {DocumentStatus.UPLOADED, DocumentStatus.PROCESSING}:
            raise ValueError("document must be uploaded/processing before ready")
        return replace(
            self,
            status=DocumentStatus.READY,
            chunk_count=chunk_count,
            processed_at=datetime.now(timezone.utc),
            error_message=None,
        )

    def mark_failed(self, *, error_message: str) -> "Document":
        return replace(
            self,
            status=DocumentStatus.FAILED,
            processed_at=datetime.now(timezone.utc),
            error_message=error_message,
        )
