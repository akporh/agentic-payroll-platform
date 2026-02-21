"""fix salary_definition to workspace-scoped

Revision ID: a2ae0981bef9
Revises: bbca8050dd33
Create Date: 2026-02-17 23:12:36.638389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2ae0981bef9'
down_revision: Union[str, Sequence[str], None] = 'bbca8050dd33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Add workspace scope + metadata
    op.add_column(
        "salary_definition",
        sa.Column("workspace_id", sa.UUID(), nullable=True),
    )

    op.add_column(
        "salary_definition",
        sa.Column("name", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "salary_definition",
        sa.Column("schema_version", sa.Integer(), nullable=True),
    )

    op.add_column(
        "salary_definition",
        sa.Column("effective_from", sa.Date(), nullable=True),
    )

    op.add_column(
        "salary_definition",
        sa.Column("effective_to", sa.Date(), nullable=True),
    )

    # Foreign key to workspace
    op.create_foreign_key(
        "salary_definition_workspace_id_fkey",
        "salary_definition",
        "workspace",
        ["workspace_id"],
        ["workspace_id"],
    )


def downgrade() -> None:

    op.drop_constraint(
        "salary_definition_workspace_id_fkey",
        "salary_definition",
        type_="foreignkey",
    )

    op.drop_column("salary_definition", "effective_to")
    op.drop_column("salary_definition", "effective_from")
    op.drop_column("salary_definition", "schema_version")
    op.drop_column("salary_definition", "name")
    op.drop_column("salary_definition", "workspace_id")

