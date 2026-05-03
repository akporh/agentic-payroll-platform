"""Add non_taxable and paye_addition component_class values; seed PAYE_ONLY_ADDITIONS row.

Sprint 12 M1 + M2 arch-council binding decisions:
  - D-M1-1: non_taxable class excluded from GROSS_PAY, included in NET_PAY via net_formula sweep.
  - D-M2-2: paye_addition class used for PAYE_ONLY_ADDITIONS aggregate (priority 95).
  - component_class column gains a CHECK constraint covering all known live values + new ones.

Revision ID: c5d6e7f8a9b0
Revises: f9a0b1c2d3e4
Create Date: 2026-05-03 00:00:00.000000
"""
import uuid
from alembic import op
import sqlalchemy as sa

revision: str = "c5d6e7f8a9b0"
down_revision: str = "f9a0b1c2d3e4"
branch_labels = None
depends_on = None

_ALLOWED_CLASSES = (
    "earning",
    "statutory_deduction",
    "aggregate",
    "final",
    "statutory_relief",
    "employer_cost",
    "non_taxable",
    "paye_addition",
)

_PAYE_ONLY_ADDITIONS_ID = "c5d6e7f8-a9b0-4000-8000-c5d6e7f8a9b0"


def upgrade() -> None:
    conn = op.get_bind()

    # Pre-check: abort if any live component_class value is outside the allowed set.
    placeholders = ", ".join(f"'{v}'" for v in _ALLOWED_CLASSES)
    result = conn.execute(sa.text(
        f"SELECT DISTINCT component_class FROM component_metadata "
        f"WHERE component_class IS NOT NULL AND component_class NOT IN ({placeholders})"
    ))
    violations = [row[0] for row in result]
    if violations:
        raise RuntimeError(
            f"Migration aborted: component_metadata contains unrecognised component_class "
            f"values {violations!r}. Clean up these rows before applying this migration."
        )

    # Add CHECK constraint — allows NULL (existing unclassified rows) and all known values.
    op.execute(sa.text(
        """
        DO $$ BEGIN
            ALTER TABLE component_metadata
                ADD CONSTRAINT ck_component_metadata_class
                CHECK (
                    component_class IS NULL OR component_class IN (
                        'earning', 'statutory_deduction', 'aggregate', 'final',
                        'statutory_relief', 'employer_cost', 'non_taxable', 'paye_addition'
                    )
                );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
        """
    ))

    # Seed PAYE_ONLY_ADDITIONS component_metadata row (M2).
    # Priority 95: after rule-injected earnings (50), before TAXABLE_INCOME (300).
    # class 'paye_addition' ensures this row is NOT swept by sum_earnings, net_formula,
    # or any statutory_deduction aggregation — only _handle_taxable_income reads it.
    conn.execute(sa.text(
        """
        INSERT INTO component_metadata (
            component_metadata_id,
            component_code,
            country_code,
            version,
            metadata_json,
            effective_from,
            is_active,
            component_class,
            calculation_method,
            execution_priority
        )
        VALUES (
            :id,
            'PAYE_ONLY_ADDITIONS',
            'NG',
            1,
            '{}',
            '2026-01-01',
            true,
            'paye_addition',
            'sum_paye_only_inputs',
            95
        )
        ON CONFLICT DO NOTHING
        """
    ), {"id": _PAYE_ONLY_ADDITIONS_ID})


def downgrade() -> None:
    conn = op.get_bind()

    # Pre-check: refuse to downgrade if any live rows use the new classes.
    result = conn.execute(sa.text(
        "SELECT COUNT(*) FROM component_metadata "
        "WHERE component_class IN ('non_taxable', 'paye_addition')"
    ))
    count = result.scalar()
    if count and count > 0:
        raise RuntimeError(
            f"Downgrade aborted: {count} component_metadata row(s) use 'non_taxable' or "
            f"'paye_addition' component_class. Remove or reclassify them before downgrading."
        )

    # Remove PAYE_ONLY_ADDITIONS seed row.
    conn.execute(sa.text(
        "DELETE FROM component_metadata WHERE component_code = 'PAYE_ONLY_ADDITIONS' "
        "AND country_code = 'NG' AND calculation_method = 'sum_paye_only_inputs'"
    ))

    # Drop CHECK constraint.
    op.execute(sa.text(
        """
        DO $$ BEGIN
            ALTER TABLE component_metadata DROP CONSTRAINT ck_component_metadata_class;
        EXCEPTION WHEN undefined_object THEN NULL;
        END $$
        """
    ))
