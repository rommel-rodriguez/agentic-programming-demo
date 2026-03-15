import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence import SQLAlchemyAttachmentMetadata
from app.domain.models import DocumentPurpose

pytestmark = pytest.mark.usefixtures("mappers")


@pytest.mark.asyncio
async def test_attachment_basic(in_memory_session_factory):
    session: AsyncSession = in_memory_session_factory()
    attachments = SQLAlchemyAttachmentMetadata(session)
    stmt1 = text("SELECT * FROM documents")
    result1 = await session.execute(stmt1)
    seq1 = result1.fetchall()
    assert len(seq1) == 0  # Check that the table is empty
    saved_uuid = await attachments.register_pending(
        content_type="application/pdf",
        original_filename="fake_filename",
        purpose=DocumentPurpose.INVOICE,
        size_bytes=1024,
        user_id=1,
    )
    result2 = await session.execute(stmt1)
    seq2 = result2.fetchall()
    assert len(seq2) == 1
