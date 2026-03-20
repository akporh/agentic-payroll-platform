"""sequential component execution prep

Phase 1 — extend component_metadata, statutory_rule, payroll_result
Phase 3 — populate execution metadata for Nigerian components

Revision ID: e1f2a3b4c5d6
Revises: d3e4f5a6b7c8
Create Date: 2026-03-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'd3e4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------ #
    # Phase 1a — extend component_metadata                                #
    # ------------------------------------------------------------------ #
    op.add_column('component_metadata', sa.Column('component_class', sa.Text(), nullable=True))
    op.add_column('component_metadata', sa.Column('calculation_method', sa.Text(), nullable=True))
    op.add_column('component_metadata', sa.Column('execution_priority', sa.Integer(), nullable=True))

    # ------------------------------------------------------------------ #
    # Phase 1b — extend statutory_rule                                    #
    # ------------------------------------------------------------------ #
    op.add_column('statutory_rule', sa.Column('country_code', sa.String(10), nullable=True))

    op.execute("""
        UPDATE statutory_rule
        SET country_code = 'NG'
        WHERE state = 'FIRS'
    """)

    # ------------------------------------------------------------------ #
    # Phase 1c — extend payroll_result                                    #
    # ------------------------------------------------------------------ #
    op.add_column(
        'payroll_result',
        sa.Column('component_trace_jsonb', sa.dialects.postgresql.JSONB(), nullable=True),
    )

    # ------------------------------------------------------------------ #
    # Phase 3 — populate execution metadata for Nigerian components       #
    # ------------------------------------------------------------------ #
    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'earning',
            calculation_method = 'salary_component',
            execution_priority = 10
        WHERE component_code = 'BASIC'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'earning',
            calculation_method = 'salary_component',
            execution_priority = 20
        WHERE component_code = 'HOUSING'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'earning',
            calculation_method = 'salary_component',
            execution_priority = 30
        WHERE component_code = 'TRANSPORT'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'earning',
            calculation_method = 'salary_component',
            execution_priority = 40
        WHERE component_code = 'CONSOLIDATED_ALLOWANCE'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'aggregate',
            calculation_method = 'sum_earnings',
            execution_priority = 100
        WHERE component_code = 'GROSS_PAY'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'statutory_deduction',
            calculation_method = 'pension_rule',
            execution_priority = 200
        WHERE component_code = 'PENSION_EMPLOYEE'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'statutory_deduction',
            calculation_method = 'paye_rule',
            execution_priority = 400
        WHERE component_code = 'PAYE'
          AND country_code   = 'NG'
    """)

    op.execute("""
        UPDATE component_metadata
        SET
            component_class    = 'final',
            calculation_method = 'net_formula',
            execution_priority = 500
        WHERE component_code = 'NET_PAY'
          AND country_code   = 'NG'
    """)


def downgrade():
    # Reverse Phase 3 data (clear populated values)
    op.execute("""
        UPDATE component_metadata
        SET component_class    = NULL,
            calculation_method = NULL,
            execution_priority = NULL
        WHERE country_code = 'NG'
          AND component_code IN (
              'BASIC', 'HOUSING', 'TRANSPORT', 'CONSOLIDATED_ALLOWANCE',
              'GROSS_PAY', 'PENSION_EMPLOYEE', 'PAYE', 'NET_PAY'
          )
    """)

    # Reverse Phase 1c
    op.drop_column('payroll_result', 'component_trace_jsonb')

    # Reverse Phase 1b
    op.execute("UPDATE statutory_rule SET country_code = NULL")
    op.drop_column('statutory_rule', 'country_code')

    # Reverse Phase 1a
    op.drop_column('component_metadata', 'execution_priority')
    op.drop_column('component_metadata', 'calculation_method')
    op.drop_column('component_metadata', 'component_class')
