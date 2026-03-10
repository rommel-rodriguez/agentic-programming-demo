"""change id type to uuid for documents

Revision ID: 40bc4ca5a08d
Revises: ecfe9e882fdb
Create Date: 2026-03-10 08:51:36.158946

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "40bc4ca5a08d"
down_revision: Union[str, Sequence[str], None] = "ecfe9e882fdb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 2) Pre-check existing data before changing VARCHAR -> UUID
UUID_RE = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    invalid_count = bind.execute(
        sa.text(
            """
            SELECT COUNT(*) 
            FROM documents 
            WHERE id IS NULL 
                OR id !~* :uuid_re
            """
        ),
        {"uuid_re": UUID_RE},
    ).scalar_one()
    if invalid_count > 0:
        samples = (
            bind.execute(
                sa.text(
                    """
                SELECT id 
                FROM documents
                WHERE id IS NULL
                    OR id !~* :uuid_re
                LIMIT 5
                """
                ),
                {"uuid_re": UUID_RE},
            )
            .scalars()
            .all()
        )
        raise RuntimeError(
            f"Aborting migration: {invalid_count} invalid documents.id values. Samples: {samples}"
        )
    op.alter_column(
        "documents",
        "id",
        existing_type=sa.String(length=36),
        type_=sa.Uuid(),
        existing_nullable=False,
        postgresql_using="id::uuid",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "documents",
        "id",
        existing_type=sa.Uuid(),
        type_=sa.String(length=36),
        existing_nullable=False,
        postgresql_using="id::text",
    )
