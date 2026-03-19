from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.domain.models import DocumentPurpose
from app.entrypoints.webapp.dependencies import (
    get_register_attachment_uc,
    get_upload_attachment_uc,
)
from app.entrypoints.webapp.models.invoice import (
    RunIn,
    UploadInitIn,
    UploadInitOut,
)
from app.services.commands import (
    RegisterAttachmentCommand,
    UploadAttachmentContentCommand,
)
from app.services.invoices import RegisterAttachment

router = APIRouter(tags=["agent-workflows", "invoice-parsing"])


@router.post("/attachments/init", response_model=UploadInitOut)
async def init_upload(
    payload: UploadInitIn,
    register_attachment_uc: RegisterAttachment = Depends(get_register_attachment_uc),
):
    # TODO: somehow decode the auth token and get the user_id before creating the
    # command for the service. Auth token must be in the Authentication Header
    # NOTE: Settting the purpose here as this is not a generic upload endpoint, tho
    # it might be better to make this series of upload endpoints be generic in the future.
    purpose = DocumentPurpose.INVOICE
    fake_user_id = 1  # NOTE: Get this for the Authorization header somehow.
    cmd = RegisterAttachmentCommand(
        user_id=fake_user_id,
        content_type=payload.content_type,
        original_filename=payload.original_filename,
        purpose=purpose,
        size_bytes=payload.size_bytes,
    )
    id_ = await register_attachment_uc(cmd)
    # DB: insert attachment with status='pending_upload' + metadata
    return UploadInitOut(id=id_)


@router.put("/attachments/{id_}/content")
async def upload_content(
    id_: str, file: UploadFile = File(...), upload_uc=Depends(get_upload_attachment_uc)
):

    try:
        attachment_id = UUID(id_)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Must be have a valid document id")
    # TODO: This check should not be a HTTP layer responsibility, delegate this for
    # the services to take care off.
    # if file.content_type != "application/pdf":
    #     raise HTTPException(status_code=400, detail="Must be PDF file")
    content_type = str(file.content_type) or "missing-content-type"
    content = await file.read()

    cmd = UploadAttachmentContentCommand(
        user_id=1,
        attachment_id=attachment_id,
        content_type=content_type,
        content=content,
        original_filename="Fake original filename",
    )
    try:
        await upload_uc(cmd)
    except Exception as e:
        raise HTTPException(status_code=500, detail="")
    # TODO: Implement service, or just code snippet, that takes care of media storage
    # storage.save(id, file)
    # DB: set status='uploaded'
    return {"ok": True}


@router.post("/runs")
async def create_run(payload: RunIn):
    # Validate attachment exists + belongs to user + status == 'uploaded'
    # DB: create application, link resume_attachment_id
    return {"application_id": "..."}
