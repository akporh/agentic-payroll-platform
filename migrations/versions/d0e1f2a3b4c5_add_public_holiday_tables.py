"""Add national_public_holiday and workspace_public_holiday tables (PH-1)

Revision ID: d0e1f2a3b4c5
Revises: b0c1d2e3f4a5
Create Date: 2026-04-13

Seeds NGA Tier-1 public holidays for 2026.

"""
from typing import Sequence, Union

from alembic import op


revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── national_public_holiday ───────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS national_public_holiday (
            holiday_id      UUID    NOT NULL DEFAULT gen_random_uuid(),
            country_code    TEXT    NOT NULL,
            holiday_date    DATE    NOT NULL,
            name            TEXT    NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT pk_national_public_holiday           PRIMARY KEY (holiday_id),
            CONSTRAINT uq_national_public_holiday_date      UNIQUE (country_code, holiday_date)
        );
    """)

    # ── workspace_public_holiday ──────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS workspace_public_holiday (
            holiday_id      UUID    NOT NULL DEFAULT gen_random_uuid(),
            workspace_id    UUID    NOT NULL REFERENCES workspace(workspace_id),
            holiday_date    DATE    NOT NULL,
            name            TEXT    NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT pk_workspace_public_holiday          PRIMARY KEY (holiday_id),
            CONSTRAINT uq_workspace_public_holiday_date     UNIQUE (workspace_id, holiday_date)
        );
    """)

    # ── NGA 2026 Tier-1 seeds ─────────────────────────────────────────────────
    # Remove any stale rows for NG 2026 before inserting correct data
    op.execute("""
        DELETE FROM national_public_holiday
        WHERE country_code = 'NG'
          AND EXTRACT(YEAR FROM holiday_date) = 2026;
    """)

    op.execute("""
        INSERT INTO national_public_holiday (country_code, holiday_date, name)
        VALUES
            ('NG', '2026-01-01', 'New Year''s Day'),
            ('NG', '2026-01-20', 'Armed Forces Remembrance Day'),
            ('NG', '2026-03-20', 'Eid al-Fitr (Day 1)'),
            ('NG', '2026-03-21', 'Eid al-Fitr (Day 2)'),
            ('NG', '2026-04-03', 'Good Friday'),
            ('NG', '2026-04-06', 'Easter Monday'),
            ('NG', '2026-05-01', 'Workers'' Day'),
            ('NG', '2026-05-27', 'Eid el-Kabir (Day 1)'),
            ('NG', '2026-05-28', 'Eid el-Kabir (Day 2)'),
            ('NG', '2026-06-12', 'Democracy Day'),
            ('NG', '2026-08-25', 'Eid el-Maulud'),
            ('NG', '2026-10-01', 'Independence Day'),
            ('NG', '2026-12-25', 'Christmas Day'),
            ('NG', '2026-12-26', 'Boxing Day')
        ON CONFLICT (country_code, holiday_date) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DELETE FROM national_public_holiday WHERE country_code = 'NG' AND EXTRACT(YEAR FROM holiday_date) = 2026;")
    op.execute("DROP TABLE IF EXISTS workspace_public_holiday;")
    op.execute("DROP TABLE IF EXISTS national_public_holiday;")
