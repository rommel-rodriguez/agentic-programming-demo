from uuid import UUID


class StorageKeyBuilder:
    def __init__(self, env_prefix: str):
        self.env_prefix = env_prefix

    def attachment(
        self, *, tenant_id: str, attachment_id: UUID, yyyy: int, mm: int
    ) -> str:
        return f"{self.env_prefix}/tenants/{tenant_id}/attachments/{yyyy:04d}/{mm:02d}/{attachment_id}"
