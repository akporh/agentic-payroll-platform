"""add platform attendance template tables with v1 seed data

Revision ID: aa1bb2cc3dd4
Revises: 5e6f7a8b9c0d
Create Date: 2026-05-13
"""
from typing import Union, Sequence
from alembic import op
import sqlalchemy as sa

revision: str = "aa1bb2cc3dd4"
down_revision: Union[str, Sequence[str], None] = "5e6f7a8b9c0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS platform_attendance_template_version (
            version_tag  VARCHAR(10) PRIMARY KEY,
            released_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            notes        VARCHAR(500)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS platform_attendance_code_template (
            client_code           VARCHAR(20) PRIMARY KEY,
            description           VARCHAR(200),
            category              VARCHAR(10) NOT NULL
                                  CHECK (category IN ('WORK','LEAVE','OT','SHIFT')),
            is_active             BOOLEAN NOT NULL DEFAULT TRUE,
            introduced_in_version VARCHAR(10) NOT NULL
                                  REFERENCES platform_attendance_template_version(version_tag),
            created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS platform_attendance_policy_template (
            client_code                  VARCHAR(20) PRIMARY KEY
                                         REFERENCES platform_attendance_code_template(client_code),
            counts_as_paid               BOOLEAN NOT NULL DEFAULT TRUE,
            counts_towards_ot_threshold  BOOLEAN NOT NULL DEFAULT TRUE,
            hours_equivalent             NUMERIC(5,2),
            unit_fraction                NUMERIC(5,4),
            eligible_for_shift_allowance BOOLEAN NOT NULL DEFAULT FALSE,
            eligible_for_ot              BOOLEAN NOT NULL DEFAULT FALSE,
            introduced_in_version        VARCHAR(10) NOT NULL
                                         REFERENCES platform_attendance_template_version(version_tag),
            created_at                   TIMESTAMPTZ NOT NULL DEFAULT now(),
            CHECK (hours_equivalent IS NULL OR hours_equivalent > 0),
            CHECK (unit_fraction IS NULL OR (unit_fraction > 0 AND unit_fraction <= 1)),
            CHECK (NOT (counts_as_paid = FALSE AND counts_towards_ot_threshold = TRUE)),
            CHECK (NOT (hours_equivalent IS NOT NULL AND unit_fraction IS NOT NULL))
        )
    """)

    # Seed v1
    op.execute("""
        INSERT INTO platform_attendance_template_version (version_tag, notes)
        VALUES ('v1', 'Initial platform defaults')
        ON CONFLICT (version_tag) DO NOTHING
    """)

    op.execute("""
        INSERT INTO platform_attendance_code_template
            (client_code, description, category, introduced_in_version)
        VALUES
            ('L',   'Annual Leave',             'LEAVE', 'v1'),
            ('SLA', 'Sick Leave - Partial Day',  'LEAVE', 'v1'),
            ('SLD', 'Sick Leave - Full Day',     'LEAVE', 'v1'),
            ('SLN', 'Sick Leave - Night',        'LEAVE', 'v1'),
            ('P',   'Paternity Leave',           'LEAVE', 'v1'),
            ('M',   'Maternity Leave',           'LEAVE', 'v1'),
            ('C',   'Compassionate Leave',       'LEAVE', 'v1')
        ON CONFLICT (client_code) DO NOTHING
    """)

    op.execute("""
        INSERT INTO platform_attendance_policy_template
            (client_code, counts_as_paid, counts_towards_ot_threshold,
             hours_equivalent, unit_fraction, introduced_in_version)
        VALUES
            ('L',   TRUE, TRUE, NULL, 1.0,  'v1'),
            ('SLA', TRUE, TRUE, 6.50, NULL, 'v1'),
            ('SLD', TRUE, TRUE, 8.00, NULL, 'v1'),
            ('SLN', TRUE, TRUE, 11.0, NULL, 'v1'),
            ('P',   TRUE, TRUE, 8.00, NULL, 'v1'),
            ('M',   TRUE, TRUE, 8.00, NULL, 'v1'),
            ('C',   TRUE, TRUE, 8.00, NULL, 'v1')
        ON CONFLICT (client_code) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS platform_attendance_policy_template")
    op.execute("DROP TABLE IF EXISTS platform_attendance_code_template")
    op.execute("DROP TABLE IF EXISTS platform_attendance_template_version")
