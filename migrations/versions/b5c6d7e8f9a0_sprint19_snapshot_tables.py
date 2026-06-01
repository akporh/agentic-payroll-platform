"""Sprint 19 — snapshot tables + salary_inputs_snapshot

Revision ID: b5c6d7e8f9a0
Revises: a4b5c6d7e8f9
Create Date: 2026-06-01

Creates three snapshot tables frozen at run time and adds a per-result salary
audit column.  Together these ensure retry determinism and full audit traceability.

Tables created:
    employee_contract_snapshot
    component_metadata_snapshot
    client_component_metadata_snapshot

Column added:
    payroll_result.salary_inputs_snapshot  JSONB NOT NULL
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "b5c6d7e8f9a0"
down_revision = "a4b5c6d7e8f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. employee_contract_snapshot ─────────────────────────────────────────
    # D1: salary_definition_id frozen; retry joins salary_definition live on it.
    # D2: UNIQUE (payroll_run_id, employee_id) enforces one row per employee per run.
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE employee_contract_snapshot (
                snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                payroll_run_id      UUID NOT NULL
                                        REFERENCES payroll_run(payroll_run_id),
                employee_id         UUID NOT NULL
                                        REFERENCES employee(employee_id),
                salary_definition_id UUID NOT NULL,
                components_jsonb    JSONB NOT NULL,
                contract_start      DATE,
                contract_end        DATE,
                shift_type          VARCHAR(10),
                grade_id            UUID,
                grade_jsonb         JSONB,
                UNIQUE (payroll_run_id, employee_id)
            );
        EXCEPTION WHEN duplicate_table THEN NULL;
        END $$;
    """)

    # ── 2. component_metadata_snapshot ────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE component_metadata_snapshot (
                snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                payroll_run_id      UUID NOT NULL
                                        REFERENCES payroll_run(payroll_run_id),
                component_code      TEXT NOT NULL,
                component_class     TEXT,
                calculation_method  TEXT,
                execution_priority  INTEGER,
                is_active           BOOLEAN,
                metadata_json       JSONB,
                UNIQUE (payroll_run_id, component_code)
            );
        EXCEPTION WHEN duplicate_table THEN NULL;
        END $$;
    """)

    # ── 3. client_component_metadata_snapshot ─────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE client_component_metadata_snapshot (
                snapshot_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                payroll_run_id      UUID NOT NULL
                                        REFERENCES payroll_run(payroll_run_id),
                workspace_id        UUID NOT NULL,
                component_code      TEXT NOT NULL,
                overrides_json      JSONB,
                proration_strategy  VARCHAR(50),
                UNIQUE (payroll_run_id, component_code)
            );
        EXCEPTION WHEN duplicate_table THEN NULL;
        END $$;
    """)

    # ── 4. salary_inputs_snapshot on payroll_result ───────────────────────────
    # Two-step NOT NULL: add with default, then drop default so future rows must
    # supply the value explicitly (existing rows get '{}').
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE payroll_result
                ADD COLUMN salary_inputs_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    op.execute("""
        ALTER TABLE payroll_result
            ALTER COLUMN salary_inputs_snapshot DROP DEFAULT;
    """)


def downgrade() -> None:
    # Drop salary_inputs_snapshot column first (no FK dependencies)
    op.execute("""
        ALTER TABLE payroll_result
            DROP COLUMN IF EXISTS salary_inputs_snapshot;
    """)

    # Drop snapshot tables in reverse FK order
    op.execute("DROP TABLE IF EXISTS client_component_metadata_snapshot;")
    op.execute("DROP TABLE IF EXISTS component_metadata_snapshot;")
    op.execute("DROP TABLE IF EXISTS employee_contract_snapshot;")
