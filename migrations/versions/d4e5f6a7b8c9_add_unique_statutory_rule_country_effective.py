"""Add UNIQUE constraint on statutory_rule(country_code, effective_from)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b9
Create Date: 2026-04-08 00:03:00.000000

Prevents non-deterministic statutory rate selection caused by duplicate
(country_code, effective_from) rows. Without this constraint the payroll
run query uses LIMIT 1 + ORDER BY and silently picks an arbitrary row
when duplicates exist, producing wrong PAYE / pension / NHF calculations.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fail fast if duplicates already exist so the migration never silently
    # applies on a database with pre-existing bad data.
    op.execute(
        sa.text("""
        DO $$ BEGIN
          IF EXISTS (
            SELECT 1
            FROM statutory_rule
            GROUP BY country_code, effective_from
            HAVING COUNT(*) > 1
          ) THEN
            RAISE EXCEPTION
              'Cannot add UNIQUE constraint: duplicate (country_code, effective_from) rows exist in statutory_rule';
          END IF;
        END $$;
        """)
    )

    op.create_unique_constraint(
        "uq_statutory_rule_country_effective",
        "statutory_rule",
        ["country_code", "effective_from"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_statutory_rule_country_effective",
        "statutory_rule",
        type_="unique",
    )
