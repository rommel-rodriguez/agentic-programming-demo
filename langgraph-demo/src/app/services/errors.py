class ApplicationError(Exception):
    code = "application_error"


class UnsupportedMimeTypeError(ApplicationError):
    code = "unsupported_mime_type"


class AttachmentNotPendingError(ApplicationError):
    code = "attachment_not_pending"


class StorageUnavailableError(ApplicationError):
    code = "storage_unavailable"


class AttachmentMetadataUpdateError(ApplicationError):
    code = "attachment_metadata_update_error"


class AttachmentSizeBytesTooBig(ApplicationError):
    code = "attachment_size_bytes_too_big"
