from app.services.invoices import UploadAttachmentContent


def build_upload_attachment_use_case(*, storage, uow) -> UploadAttachmentContent:
    return UploadAttachmentContent(
        storage=storage,
        uow=uow,
    )
