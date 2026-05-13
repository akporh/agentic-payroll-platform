"""add timesheet_enabled to workspace_payroll_config and attendance_template_version to workspace

Revision ID: dd4ee5ff6aa7
Revises: cc3dd4ee5ff6
Create Date: 2026-05-13
"""
from typing import Union, Sequence
from alembic import op

revision: str = "dd4ee5ff6aa7"
down_revision: Union[str, Sequence[str], None] = "cc3dd4ee5ff6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE workspace_payroll_config
                ADD COLUMN timesheet_enabled BOOLEAN NOT NULL DEFAULT FALSE;
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$
    """)

    op.execute("""
        DO $$ BEGIN
            ALTER TABLE workspace
                ADD COLUMN attendance_template_version VARCHAR(10)
                REFERENCES platform_attendance_template_version(version_tag);
        EXCEPTION WHEN duplicate_column THEN NULL;
        END $$
    """)


def downgrade() -> None:
    op.execute("""
        DO $$ BEGIN
            ALTER TABLE workspace DROP COLUMN attendance_template_version;
        EXCEPTION WHEN undefined_column THEN NULL;
        END $$
    """)

    op.execute("""
        DO $$ BEGIN
            ALTER TABLE workspace_payroll_config DROP COLUMN timesheet_enabled;
        EXCEPTION WHEN undefined_column THEN NULL;
        END $$
    """)
