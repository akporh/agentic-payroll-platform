"""enforce salary definition json object structure

Revision ID: c789a9f78a41
Revises: 2899259558ff
Create Date: 2026-02-19 07:30:25.072415

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c789a9f78a41'
down_revision: Union[str, Sequence[str], None] = 'e178ad859b44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # Ensure salary_definition.components_jsonb is always an object
    op.execute("""
    ALTER TABLE salary_definition
    ADD CONSTRAINT chk_salary_components_is_object
    CHECK (jsonb_typeof(components_jsonb) = 'object');
    """)

    # Require BASIC key exists
    op.execute("""
    ALTER TABLE salary_definition
    ADD CONSTRAINT chk_salary_definition_basic_required
    CHECK (components_jsonb ? 'BASIC');
    """)


def downgrade():
    pass
