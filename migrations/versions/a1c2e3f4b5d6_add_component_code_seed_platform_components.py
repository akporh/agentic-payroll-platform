"""Add component_code to component_metadata, seed platform components, create client_component_metadata

Revision ID: a1c2e3f4b5d6
Revises: f1a2b3c4d5e6
Create Date: 2026-03-09

Changes
-------
1. Rename component_metadata.rules_jsonb → metadata_json  (aligns column
   name with its actual semantic role; rules_jsonb was a legacy name).

2. Add component_metadata.component_code TEXT NOT NULL.
   Drop the old unique index on (country_code, version) — it was too broad;
   replace with a tighter index on (component_code, country_code, version).

3. Seed five platform-level statutory components for Nigeria (NG, v1):
   PAYE, PENSION_EMPLOYEE, PENSION_EMPLOYER, GROSS_PAY, NET_PAY.

4. Create client_component_metadata table.
   Client components (BASIC, HOUSING, TRANSPORT, BONUS, etc.) are inserted
   during workspace onboarding and are scoped to a workspace_id.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1c2e3f4b5d6"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # 1. Rename rules_jsonb → metadata_json
    # ------------------------------------------------------------------
    op.alter_column(
        "component_metadata",
        "rules_jsonb",
        new_column_name="metadata_json",
    )

    # ------------------------------------------------------------------
    # 2a. Add component_code column
    #     Use a temporary server_default so PostgreSQL can backfill any
    #     existing rows before we enforce NOT NULL.
    # ------------------------------------------------------------------
    op.add_column(
        "component_metadata",
        sa.Column(
            "component_code",
            sa.Text(),
            nullable=False,
            server_default="",
        ),
    )
    # Remove the temporary default — future inserts must supply the value.
    op.alter_column("component_metadata", "component_code", server_default=None)

    # ------------------------------------------------------------------
    # 2b. Replace the old (country_code, version) unique index with the
    #     more specific (component_code, country_code, version) index.
    # ------------------------------------------------------------------
    op.drop_index(
        "uq_component_metadata_country_version",
        table_name="component_metadata",
        if_exists=True,
    )
    op.create_index(
        "uq_component_metadata_code_country_version",
        "component_metadata",
        ["component_code", "country_code", "version"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # 3. Seed platform-level statutory components (Nigeria, v1)
    # ------------------------------------------------------------------
    op.execute("""
        INSERT INTO component_metadata
            (component_metadata_id, component_code, country_code, version,
             metadata_json, effective_from, is_active)
        VALUES
        (
            gen_random_uuid(), 'PAYE', 'NG', 1,
            '{
              "financial_role": {"category": "deduction", "affects_gross": false, "net_effect": "decrease"},
              "legal_role":     {"is_statutory": true, "compliance_category": "income_tax"},
              "engine_behavior": {"derived_node": true}
            }'::jsonb,
            '2026-01-01', true
        ),
        (
            gen_random_uuid(), 'PENSION_EMPLOYEE', 'NG', 1,
            '{
              "financial_role": {"category": "deduction", "affects_gross": false, "net_effect": "decrease"},
              "legal_role":     {"is_statutory": true, "compliance_category": "pension_employee"},
              "engine_behavior": {"derived_node": true}
            }'::jsonb,
            '2026-01-01', true
        ),
        (
            gen_random_uuid(), 'PENSION_EMPLOYER', 'NG', 1,
            '{
              "financial_role": {"category": "employer_cost", "affects_gross": false, "net_effect": "none"},
              "legal_role":     {"is_statutory": true, "compliance_category": "pension_employer"},
              "engine_behavior": {"derived_node": true}
            }'::jsonb,
            '2026-01-01', true
        ),
        (
            gen_random_uuid(), 'GROSS_PAY', 'NG', 1,
            '{
              "financial_role": {"category": "aggregate", "affects_gross": false, "net_effect": "none"},
              "engine_behavior": {"derived_node": true}
            }'::jsonb,
            '2026-01-01', true
        ),
        (
            gen_random_uuid(), 'NET_PAY', 'NG', 1,
            '{
              "financial_role": {"category": "aggregate", "affects_gross": false, "net_effect": "none"},
              "engine_behavior": {"final_node": true}
            }'::jsonb,
            '2026-01-01', true
        );
    """)

    # ------------------------------------------------------------------
    # 4. Create client_component_metadata table
    #    Scoped to a workspace; populated during onboarding.
    # ------------------------------------------------------------------
    op.create_table(
        "client_component_metadata",
        sa.Column(
            "client_component_metadata_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "workspace_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("component_code", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_foreign_key(
        "fk_client_component_metadata_workspace",
        "client_component_metadata",
        "workspace",
        ["workspace_id"],
        ["workspace_id"],
    )

    op.create_index(
        "uq_client_component_metadata_code_workspace",
        "client_component_metadata",
        ["workspace_id", "component_code"],
        unique=True,
    )


def downgrade() -> None:
    # 4. Drop client_component_metadata
    op.drop_index(
        "uq_client_component_metadata_code_workspace",
        table_name="client_component_metadata",
    )
    op.drop_constraint(
        "fk_client_component_metadata_workspace",
        "client_component_metadata",
        type_="foreignkey",
    )
    op.drop_table("client_component_metadata")

    # 3. Remove seeded rows
    op.execute("""
        DELETE FROM component_metadata
        WHERE component_code IN
            ('PAYE', 'PENSION_EMPLOYEE', 'PENSION_EMPLOYER', 'GROSS_PAY', 'NET_PAY')
        AND country_code = 'NG'
        AND version = 1;
    """)

    # 2b. Restore old unique index
    op.drop_index(
        "uq_component_metadata_code_country_version",
        table_name="component_metadata",
    )
    op.create_index(
        "uq_component_metadata_country_version",
        "component_metadata",
        ["country_code", "version"],
        unique=True,
    )

    # 2a. Drop component_code column
    op.drop_column("component_metadata", "component_code")

    # 1. Rename metadata_json → rules_jsonb
    op.alter_column(
        "component_metadata",
        "metadata_json",
        new_column_name="rules_jsonb",
    )
