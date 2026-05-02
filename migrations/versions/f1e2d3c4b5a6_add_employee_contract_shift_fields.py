"""Add shift_type, state_of_tax, skill_level to employee_contract (Track O / O1)

revision ID: f1e2d3c4b5a6
Arch-council decision D1: shift_type on employee_contract (not employee) — follows contract
versioning so shift-pattern changes are captured with contract history.
Arch-council decision D2: date_engaged = employee_contract.start_date — no new column.
Arch-council decision D3: state_of_tax typed VARCHAR(50) — not extracted from encrypted JSON.
Arch-council decision D4: skill_level VARCHAR(50) free-text — FK lookup deferred.
"""

revision: str = "f1e2d3c4b5a6"
down_revision: str = "26b848abab55"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    # shift_type — values: 'DAY', '2_SHIFT', '4_SHIFT'; NULL treated as 'DAY' by engine
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract ADD COLUMN shift_type VARCHAR(10);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)

    # state_of_tax — jurisdiction code for per-employee PAYE routing (routing logic deferred)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract ADD COLUMN state_of_tax VARCHAR(50);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)

    # skill_level — workforce classification for Client B
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract ADD COLUMN skill_level VARCHAR(50);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$;
    """)

    # CHECK constraint on shift_type — enforce known values; NULL allowed (= DAY default)
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract
                ADD CONSTRAINT chk_employee_contract_shift_type
                CHECK (shift_type IN ('DAY', '2_SHIFT', '4_SHIFT'));
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)


def downgrade() -> None:
    # Warn if non-NULL values exist — data will be lost
    op.execute("""
        DO $$ DECLARE
            cnt INTEGER;
        BEGIN
            SELECT COUNT(*) INTO cnt
            FROM employee_contract
            WHERE shift_type IS NOT NULL
               OR state_of_tax IS NOT NULL
               OR skill_level IS NOT NULL;
            IF cnt > 0 THEN
                RAISE WARNING 'Downgrade will drop % employee_contract rows with non-NULL O1 fields', cnt;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            ALTER TABLE employee_contract DROP CONSTRAINT IF EXISTS chk_employee_contract_shift_type;
        END $$;
    """)

    op.execute("ALTER TABLE employee_contract DROP COLUMN IF EXISTS shift_type")
    op.execute("ALTER TABLE employee_contract DROP COLUMN IF EXISTS state_of_tax")
    op.execute("ALTER TABLE employee_contract DROP COLUMN IF EXISTS skill_level")
