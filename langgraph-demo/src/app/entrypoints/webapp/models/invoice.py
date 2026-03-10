from uuid import UUID

from pydantic import BaseModel


class UploadInitIn(BaseModel):
    original_filename: str | None = None
    content_type: str
    size_bytes: int


class UploadInitOut(BaseModel):
    id: UUID


class RunIn(BaseModel):
    full_name: str
    email: str
    resume_id: str
