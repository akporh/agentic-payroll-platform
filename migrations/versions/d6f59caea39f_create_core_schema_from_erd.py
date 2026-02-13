"""create core schema from ERD

Revision ID: d6f59caea39f
Revises: 180f891ac9d3
Create Date: 2026-02-13 11:56:52.307599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6f59caea39f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


    """Upgrade schema."""
def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("account_id", sa.UUID(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner_email", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now()),
    )

    op.create_table(
        "workspace",
        sa.Column("workspace_id", sa.UUID(), primary_key=True),
        sa.Column("account_id", sa.UUID(), sa.ForeignKey("account.account_id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("country_code", sa.String(), nullable=False),
        sa.Column("base_currency", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.func.now()),
    )

    op.create_table(
        "employee",
        sa.Column("employee_id", sa.UUID(), primary_key=True),
        sa.Column("workspace_id", sa.UUID(), sa.ForeignKey("workspace.workspace_id"), nullable=False),
        sa.Column("employee_number", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("personal_details_encrypted", sa.JSON(), nullable=True),
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("employee")
    op.drop_table("workspace")
    op.drop_table("account")
