"""change column name and nullable status for documents

Revision ID: ecfe9e882fdb
Revises: 1618c798113b
Create Date: 2026-03-10 07:50:38.180728

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ecfe9e882fdb"
down_revision: Union[str, Sequence[str], None] = "1618c798113b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_COLUMN_NAME = "original_filename"


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "documents",
        "filename",
        new_column_name=NEW_COLUMN_NAME,
    )
    op.alter_column(
        "documents",
        NEW_COLUMN_NAME,
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    null_count = bind.execute(
        sa.text("SELECT COUNT(*) FROM documents WHERE original_filename IS NULL")
    ).scalar_one()
    if null_count > 0:
        raise RuntimeError(
            f"Aborting downgrade: {null_count} rows have NULL original_filename."
        )

    op.alter_column(
        "documents",
        NEW_COLUMN_NAME,
        nullable=False,
    )
    op.alter_column(
        "documents",
        NEW_COLUMN_NAME,
        new_column_name="filename",
    )
