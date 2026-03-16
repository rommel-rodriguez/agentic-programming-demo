from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.persistence import SQLAlchemyAttachmentMetadata
from app.domain.models import Document, DocumentPurpose
from app.ports.errors import AttachmentRepositoryError

pytestmark = pytest.mark.usefixtures("mappers")


@pytest.mark.asyncio
async def test_attachment_basic(in_memory_session_factory):
    # session: AsyncSession = in_memory_session_factory()
    async with in_memory_session_factory() as session:
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

        doc = await session.get(Document, saved_uuid)
    assert doc is not None
    assert isinstance(doc.id, UUID)
    assert doc.id == saved_uuid
    assert doc.content_type == "application/pdf"


# NOTE: This is a, for now, safer version of the test_attachment_basic using a session
# fixture with safety net instead of a factory fixture.
@pytest.mark.asyncio
async def test_attachment_proto(in_memory_db_session):
    session = in_memory_db_session
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

    doc = await session.get(Document, saved_uuid)
    assert doc is not None
    assert isinstance(doc.id, UUID)
    assert doc.id == saved_uuid
    assert doc.content_type == "application/pdf"


# NOTE: Not really an integration test, move to unittests later
@pytest.mark.asyncio
async def test_attachments_raises_repository_integrity_error():
    session = Mock(spec=AsyncSession)
    session.add = Mock()
    session.flush = AsyncMock(
        side_effect=IntegrityError("stmt", "params", Exception("db"))
    )
    repo = SQLAlchemyAttachmentMetadata(session)

    with pytest.raises(AttachmentRepositoryError, match=r"integrity error"):
        await repo.register_pending(
            user_id=1,
            original_filename="x.pdf",
            content_type="application/pdf",
            size_bytes=100,
            purpose=DocumentPurpose.INVOICE,
        )

    session.add.assert_called_once()
    session.flush.assert_awaited_once()


# NOTE: Not really an integration test, move to unittests later
@pytest.mark.asyncio
async def test_attachments_raises_repository_general_error():
    session = Mock(spec=AsyncSession)
    session.add = Mock()
    session.flush = AsyncMock(
        side_effect=SQLAlchemyError("stmt", "params", Exception("db"))
    )
    repo = SQLAlchemyAttachmentMetadata(session)

    with pytest.raises(AttachmentRepositoryError, match=r"failed to register"):
        await repo.register_pending(
            user_id=1,
            original_filename="x.pdf",
            content_type="application/pdf",
            size_bytes=100,
            purpose=DocumentPurpose.INVOICE,
        )

    session.add.assert_called_once()
    session.flush.assert_awaited_once()
