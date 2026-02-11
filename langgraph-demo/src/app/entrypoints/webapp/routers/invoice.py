import logging
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.entrypoints.webapp.models.invoice import (
    RunIn,
    UploadInitIn,
    UploadInitOut,
)

router = APIRouter(tags=["agent-workflows", "invoice-parsing"])


@router.post("/attachments/init", response_model=UploadInitOut)
async def init_upload(payload: UploadInitIn):
    id = str(uuid.uuid4())
    # DB: insert attachment with status='pending_upload' + metadata
    return UploadInitOut(id=id)


@router.put("/attachments/{id}/content")
async def upload_content(id: str, file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Must be PDF file")
    # TODO: Implement service, or just code snippet, that takes care of media storage
    # storage.save(id, file)
    # DB: set status='uploaded'
    return {"ok": True}


@router.post("/runs")
async def create_run(payload: RunIn):
    # Validate attachment exists + belongs to user + status == 'uploaded'
    # DB: create application, link resume_attachment_id
    return {"application_id": "..."}
