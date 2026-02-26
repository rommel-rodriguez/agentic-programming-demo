"""add enum check contraints for documents

Revision ID: 1618c798113b
Revises: 31b0afc294f0
Create Date: 2026-02-24 22:14:33.416411

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1618c798113b"
down_revision: Union[str, Sequence[str], None] = "31b0afc294f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

VALID_STATUS = ("pending_upload", "uploaded", "processing", "ready", "failed")
VALID_PURPOSE = ("resume", "invoice", "context")


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()

    bad_status = bind.execute(
        sa.text(
            """
            SELECT id, status 
            FROM documents 
            WHERE status IS NOT NULL
             AND status NOT IN  :allowed
            """
        ).bindparams(sa.bindparam("allowed", expanding=True)),
        {"allowed": list(VALID_STATUS)},
    ).fetchall()

    bad_purpose = bind.execute(
        sa.text(
            """
            SELECT id, purpose
            FROM documents
            WHERE purpose IS NOT NULL
             AND purpose NOT IN :allowed
            """
        ).bindparams(sa.bindparam("allowed", expanding=True)),
        {"allowed": list(VALID_PURPOSE)},
    ).fetchall()

    if bad_status or bad_purpose:
        raise RuntimeError(
            f"Invalid enum data found. bad_status={bad_status}, bad_purpose={bad_purpose}"
        )

    op.create_check_constraint(
        "ck_documents_status_enum",
        "documents",
        "status IN ('pending_upload', 'uploaded','processing','ready', 'failed')",
    )

    op.create_check_constraint(
        "ck_documents_purpose_enum",
        "documents",
        "purpose IN ('resume', 'invoice','context')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("ck_documents_purpose_enum", "documents", type_="check")
    op.drop_constraint("ck_documents_status_enum", "documents", type_="check")
