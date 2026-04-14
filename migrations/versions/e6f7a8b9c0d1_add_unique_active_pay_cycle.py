"""Guard against multiple active pay cycles per workspace

Revision ID: e6f7a8b9c0d1
Revises: d4e5f6a7b8c9
Create Date: 2026-04-08 00:04:00.000000

Without this index a workspace can have multiple is_active=TRUE pay cycles.
Queries use LIMIT 1 and silently pick an arbitrary active cycle, causing
non-deterministic pay period dates and wrong proration for joiners/leavers.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e6f7a8b9c0d1"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fail fast if any workspace already has multiple active cycles.
    op.execute(
        sa.text("""
        DO $$ BEGIN
          IF EXISTS (
            SELECT 1
            FROM pay_cycle
            WHERE is_active = TRUE
            GROUP BY workspace_id
            HAVING COUNT(*) > 1
          ) THEN
            RAISE EXCEPTION
              'Cannot add unique index: multiple active pay cycles exist for at least one workspace';
          END IF;
        END $$;
        """)
    )

    op.create_index(
        "uq_pay_cycle_active",
        "pay_cycle",
        ["workspace_id"],
        unique=True,
        postgresql_where=sa.text("is_active = TRUE"),
    )


def downgrade() -> None:
    op.drop_index("uq_pay_cycle_active", table_name="pay_cycle")
