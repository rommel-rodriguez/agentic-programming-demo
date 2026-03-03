from app.services.invoices import UploadAttachmentContent


def build_upload_attachment_use_case(
    *, storage, attachments
) -> UploadAttachmentContent:
    return UploadAttachmentContent(
        storage=storage,
        attachments=attachments,
    )
