"""fix salary definition template metadata

Revision ID: e178ad859b44
Revises: 9ffee63ba8d1
Create Date: 2026-02-19 06:08:15.241144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e178ad859b44'
down_revision: Union[str, Sequence[str], None] = '9ffee63ba8d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # =========================================================
    # SALARY_DEFINITION Phase 1 Fix
    # Align template structure with ERD
    # =========================================================

    # 1. Add workspace_id (tenant boundary)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='salary_definition'
              AND column_name='workspace_id'
        ) THEN
            ALTER TABLE salary_definition
            ADD COLUMN workspace_id UUID;
        END IF;
    END $$;
    """)

    # Add FK constraint safely (only if missing)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE table_name='salary_definition'
              AND constraint_name='fk_salary_definition_workspace'
        ) THEN
            ALTER TABLE salary_definition
            ADD CONSTRAINT fk_salary_definition_workspace
            FOREIGN KEY (workspace_id)
            REFERENCES workspace(workspace_id);
        END IF;
    END $$;
    """)

    # 2. Add name (template label)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='salary_definition'
              AND column_name='name'
        ) THEN
            ALTER TABLE salary_definition
            ADD COLUMN name VARCHAR(255);
        END IF;
    END $$;
    """)

    # 3. Add schema_version (default 1)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='salary_definition'
              AND column_name='schema_version'
        ) THEN
            ALTER TABLE salary_definition
            ADD COLUMN schema_version INT DEFAULT 1;
        END IF;
    END $$;
    """)

    # 4. Add effective dating
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='salary_definition'
              AND column_name='effective_from'
        ) THEN
            ALTER TABLE salary_definition
            ADD COLUMN effective_from DATE;
        END IF;
    END $$;
    """)

    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name='salary_definition'
              AND column_name='effective_to'
        ) THEN
            ALTER TABLE salary_definition
            ADD COLUMN effective_to DATE;
        END IF;
    END $$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
