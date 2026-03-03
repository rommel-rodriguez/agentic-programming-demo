from app.ports.attachments import AttachmentMetadataPort
from app.ports.media_storage import MediaStoragePort
from app.services.commands import UploadAttachmentContentCommand


async def parse_invoice():
    pass


async def upload_attachment_content(
    cmd: UploadAttachmentContentCommand,
    *,
    storage: MediaStoragePort,
    attachments: AttachmentMetadataPort,
) -> None: ...


class UploadAttachmentContent:
    def __init__(
        self, *, storage: MediaStoragePort, attachments: AttachmentMetadataPort
    ) -> None:
        self._storage = storage
        self._attachments = attachments

    async def __call__(self, cmd: UploadAttachmentContentCommand) -> None:
        if cmd.content_type != "application/pdf":
            raise ValueError("Must be PDF file")

        exists = await self._attachments.exists_pending(cmd.attachment_id)
        if not exists:
            raise LookupError("Attachment not found or is not pending upload")

        storage_ref = await self._storage.save(
            key=cmd.attachment_id,
            content=cmd.content,
            content_type=cmd.content_type,
            original_filename=cmd.original_filename,
        )

        await self._attachments.mark_uploaded(
            attachment_id=cmd.attachment_id,
            storage_ref=storage_ref,
            content_type=cmd.content_type,
            size_bytes=len(cmd.content),
        )
