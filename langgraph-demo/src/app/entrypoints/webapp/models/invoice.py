from pydantic import BaseModel


class UploadInitIn(BaseModel):
    filename: str
    content_type: str
    size_bytes: int


class UploadInitOut(BaseModel):
    id: str


class RunIn(BaseModel):
    full_name: str
    email: str
    resume_id: str
