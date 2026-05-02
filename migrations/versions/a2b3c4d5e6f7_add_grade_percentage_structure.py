"""Add grade percentage salary structure columns (Track O / O2)

revision ID: a2b3c4d5e6f7
Arch-council decisions:
  D5: derivation is an isolated pure function called by both route and retry service.
  D6: grade pct wins when total_monthly non-null; salary_definition.components_jsonb ignored.
  D7: round-half-up each component; adjust largest to absorb residual.
"""

revision: str = "a2b3c4d5e6f7"
down_revision: str = "f1e2d3c4b5a6"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade ADD COLUMN total_monthly DECIMAL(15,2);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade ADD COLUMN basic_pct DECIMAL(5,4);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade ADD COLUMN housing_pct DECIMAL(5,4);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade ADD COLUMN transport_pct DECIMAL(5,4);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade ADD COLUMN utility_pct DECIMAL(5,4);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)

    # Completeness constraint: if total_monthly is set, all four pct columns must be
    # present and must sum to 1.0 (±0.0001 tolerance for decimal input rounding).
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade ADD CONSTRAINT chk_grade_pct_completeness CHECK (
                total_monthly IS NULL OR (
                    basic_pct IS NOT NULL
                    AND housing_pct IS NOT NULL
                    AND transport_pct IS NOT NULL
                    AND utility_pct IS NOT NULL
                    AND ABS(basic_pct + housing_pct + transport_pct + utility_pct - 1.0) < 0.0001
                )
            );
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    # Warn if any percentage-model grades exist — data will be lost
    op.execute("""
        DO $$ DECLARE
            cnt INTEGER;
        BEGIN
            SELECT COUNT(*) INTO cnt FROM grade WHERE total_monthly IS NOT NULL;
            IF cnt > 0 THEN
                RAISE WARNING 'Downgrade will drop percentage salary structure from % grade rows', cnt;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            ALTER TABLE grade DROP CONSTRAINT IF EXISTS chk_grade_pct_completeness;
        END $$;
    """)

    op.execute("ALTER TABLE grade DROP COLUMN IF EXISTS total_monthly")
    op.execute("ALTER TABLE grade DROP COLUMN IF EXISTS basic_pct")
    op.execute("ALTER TABLE grade DROP COLUMN IF EXISTS housing_pct")
    op.execute("ALTER TABLE grade DROP COLUMN IF EXISTS transport_pct")
    op.execute("ALTER TABLE grade DROP COLUMN IF EXISTS utility_pct")
