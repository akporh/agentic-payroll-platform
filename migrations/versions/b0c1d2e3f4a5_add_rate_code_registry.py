"""Add rate_code_registry table and platform OT seeds (PH-7)

Revision ID: b0c1d2e3f4a5
Revises: a9b0c1d2e3f4
Create Date: 2026-04-13

Arch-council (D-ARCH-10, OQ1):
  - is_pensionable does NOT live on this table — it lives on component_metadata.
  - Platform seeds are workspace_id IS NULL (shared across all workspaces).
  - Workspace overrides have workspace_id set; NULLS DISTINCT allows platform
    seeds to share the same code without violating the unique constraint.
  - PH_OT component_metadata row seeded here with legal_role.is_pensionable=true.

"""
from typing import Sequence, Union

from alembic import op


revision: str = "b0c1d2e3f4a5"
down_revision: Union[str, Sequence[str], None] = "a9b0c1d2e3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── rate_code_registry table ──────────────────────────────────────────────
    op.execute("""
        CREATE TABLE IF NOT EXISTS rate_code_registry (
            rate_code_id    UUID            NOT NULL DEFAULT gen_random_uuid(),
            workspace_id    UUID            REFERENCES workspace(workspace_id),
            code            TEXT            NOT NULL,
            multiplier      NUMERIC(8, 4)   NOT NULL,
            unit            TEXT            NOT NULL,
            base            TEXT            NOT NULL,
            description     TEXT            NOT NULL,
            is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),

            CONSTRAINT pk_rate_code_registry    PRIMARY KEY (rate_code_id),
            CONSTRAINT ck_rcr_unit              CHECK (unit IN ('hour', 'day')),
            CONSTRAINT ck_rcr_base              CHECK (base IN ('basic_hourly', 'basic_daily'))
        );
    """)

    # UNIQUE(workspace_id, code) with NULLS DISTINCT so platform seeds
    # (workspace_id IS NULL) are allowed alongside workspace overrides.
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = 'uq_rate_code_registry_workspace_code'
            ) THEN
                CREATE UNIQUE INDEX uq_rate_code_registry_workspace_code
                    ON rate_code_registry (workspace_id, code)
                    NULLS DISTINCT;
            END IF;
        END $$;
    """)

    # ── Platform seeds (workspace_id IS NULL) ─────────────────────────────────
    op.execute("""
        INSERT INTO rate_code_registry
            (code, workspace_id, multiplier, unit, base, description, is_active)
        VALUES
            ('OT001', NULL, 1.0000, 'hour', 'basic_hourly', 'Straight time',                       TRUE),
            ('OT002', NULL, 1.5000, 'hour', 'basic_hourly', 'Time and a half',                     TRUE),
            ('OT003', NULL, 2.0000, 'hour', 'basic_hourly', 'Double time',                         TRUE),
            ('OT004', NULL, 2.5000, 'hour', 'basic_hourly', 'Double time and a half',              TRUE),
            ('OT005', NULL, 3.2500, 'hour', 'basic_hourly', 'Triple time and a quarter (PH default)', TRUE),
            ('OT006', NULL, 3.5000, 'hour', 'basic_hourly', 'Triple time and a half',              TRUE),
            ('OT007', NULL, 3.9000, 'day',  'basic_hourly', 'Custom — triple+',                    TRUE)
        ON CONFLICT DO NOTHING;
    """)

    # ── PH_OT component_metadata seed (OQ1) ──────────────────────────────────
    # Seed the PH_OT row now so Track C can reference it.
    # NOTE: legal_role.is_pensionable is intentionally NOT set here.
    # The pension handler replaces the entire pensionable base with any
    # component that carries is_pensionable=true — adding that flag before
    # the pension handler is extended for additive mode (Track C / PH-8)
    # would collapse the pension base to zero for all periods without PH_OT.
    # The is_pensionable flag will be added atomically with the handler fix.
    op.execute("""
        INSERT INTO component_metadata
            (component_metadata_id, component_code, country_code, version,
             metadata_json, effective_from, is_active)
        SELECT
            gen_random_uuid(),
            'PH_OT',
            'NG',
            1,
            '{}'::jsonb,
            CURRENT_DATE,
            TRUE
        WHERE NOT EXISTS (
            SELECT 1 FROM component_metadata
            WHERE component_code = 'PH_OT'
              AND country_code   = 'NG'
              AND is_active      = TRUE
        );
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM component_metadata
        WHERE component_code = 'PH_OT'
          AND country_code   = 'NG';
    """)

    op.execute("DROP TABLE IF EXISTS rate_code_registry;")
