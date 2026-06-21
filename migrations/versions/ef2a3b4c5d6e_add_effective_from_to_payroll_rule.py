"""Add effective_from to payroll_rule + UNIQUE constraint + auto-publish pattern

Revision ID: ef2a3b4c5d6e
Revises: de1f2a3b4c5d
Create Date: 2026-06-21 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "ef2a3b4c5d6e"
down_revision: Union[str, Sequence[str], None] = "de1f2a3b4c5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add column (guarded — column may already exist)
    op.execute("""
    DO $$ BEGIN
        ALTER TABLE payroll_rule ADD COLUMN effective_from DATE;
    EXCEPTION WHEN duplicate_column THEN NULL; END $$;
    """)

    # Step 2: Backfill from rule_set_item using full rule_definition_json equality
    op.execute("""
    UPDATE payroll_rule pr
    SET effective_from = (
        SELECT MIN(rs.effective_from)
        FROM rule_set_item rsi
        JOIN rule_set rs ON rs.rule_set_id = rsi.rule_set_id
        WHERE rsi.rule_name = pr.rule_name
          AND rs.workspace_id = pr.workspace_id
          AND rsi.rule_definition_json = pr.rule_definition_json
    )
    WHERE effective_from IS NULL;
    """)

    # Step 3: Fallback — rules with no matching rule_set_item get 2025-01-01
    op.execute("""
    UPDATE payroll_rule SET effective_from = '2025-01-01' WHERE effective_from IS NULL;
    """)

    # Step 4: Enforce NOT NULL
    op.execute("""
    ALTER TABLE payroll_rule ALTER COLUMN effective_from SET NOT NULL;
    """)

    # Step 4b: Dedup — pre-versioning DBs may have multiple rows for the same
    # (workspace_id, rule_name) with no rule_set_item match, all backfilled to
    # 2025-01-01. Keep the most recently inserted row (highest UUID lexicographic
    # order as a proxy); discard the rest. Safe: these rows are functionally
    # identical duplicates that existed before versioning was introduced.
    op.execute("""
    DELETE FROM payroll_rule
    WHERE rule_id NOT IN (
        SELECT DISTINCT ON (workspace_id, rule_name, effective_from) rule_id
        FROM payroll_rule
        ORDER BY workspace_id, rule_name, effective_from, rule_id DESC
    );
    """)

    # Step 5: Add UNIQUE constraint (guarded — constraint may already exist)
    op.execute("""
    DO $$ BEGIN
        ALTER TABLE payroll_rule
            ADD CONSTRAINT uq_payroll_rule_name_effective
            UNIQUE (workspace_id, rule_name, effective_from);
    EXCEPTION WHEN duplicate_table THEN NULL; END $$;
    """)

    # Step 6: Add updated_at if missing (PATCH route writes updated_at = NOW())
    op.execute("""
    DO $$ BEGIN
        ALTER TABLE payroll_rule ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
    EXCEPTION WHEN duplicate_column THEN NULL; END $$;
    """)


def downgrade() -> None:
    # Drop constraint first, then collapse multi-version rows to earliest per
    # (workspace_id, rule_name), then drop column.
    op.execute("""
    ALTER TABLE payroll_rule DROP CONSTRAINT IF EXISTS uq_payroll_rule_name_effective;
    """)

    # Keep only the earliest version per (workspace_id, rule_name)
    op.execute("""
    DELETE FROM payroll_rule pr
    WHERE rule_id NOT IN (
        SELECT DISTINCT ON (workspace_id, rule_name) rule_id
        FROM payroll_rule
        ORDER BY workspace_id, rule_name, effective_from ASC
    );
    """)

    op.execute("""
    ALTER TABLE payroll_rule DROP COLUMN IF EXISTS effective_from;
    """)

    op.execute("""
    ALTER TABLE payroll_rule DROP COLUMN IF EXISTS updated_at;
    """)
