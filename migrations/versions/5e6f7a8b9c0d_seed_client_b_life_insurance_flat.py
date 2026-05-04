"""Seed Client B life insurance flat_amount override — Sprint 13 M4

Adds a client_component_metadata override row for LIFE_INSURANCE in Client B's
workspace with overrides_json = {"flat_amount": 2000}.

The life insurance handler reads flat_amount from client_meta (workspace override)
when present; otherwise falls back to rate × GROSS_PAY with a DEPRECATION warning.
This override is Client B only — the platform component_metadata seed is unchanged.

Revision ID: 5e6f7a8b9c0d
Revises: 4d5e6f7a8b9c
Create Date: 2026-05-04 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op

revision: str = "5e6f7a8b9c0d"
down_revision: Union[str, Sequence[str], None] = "4d5e6f7a8b9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Silently no-ops if workspace named 'Client B' does not exist.
    op.execute("""
    DO $$
    DECLARE _wid UUID;
    BEGIN
        SELECT workspace_id INTO _wid
        FROM workspace
        WHERE name = 'Client B'
        LIMIT 1;

        IF _wid IS NOT NULL THEN
            INSERT INTO client_component_metadata (
                client_component_metadata_id,
                workspace_id,
                component_code,
                overrides_json
            ) VALUES (
                gen_random_uuid(),
                _wid,
                'LIFE_INSURANCE',
                '{"flat_amount": 2000}'::jsonb
            )
            ON CONFLICT (workspace_id, component_code)
            DO UPDATE SET
                overrides_json = client_component_metadata.overrides_json
                                 || '{"flat_amount": 2000}'::jsonb;
        END IF;
    END $$;
    """)


def downgrade() -> None:
    # Remove flat_amount key from Client B's LIFE_INSURANCE override.
    # If the row only contained flat_amount it is left as an empty-object row
    # rather than deleted, to preserve any other keys that may have been added.
    op.execute("""
    DO $$
    DECLARE _wid UUID;
    BEGIN
        SELECT workspace_id INTO _wid
        FROM workspace
        WHERE name = 'Client B'
        LIMIT 1;

        IF _wid IS NOT NULL THEN
            UPDATE client_component_metadata
            SET overrides_json = overrides_json - 'flat_amount'
            WHERE workspace_id   = _wid
              AND component_code = 'LIFE_INSURANCE';
        END IF;
    END $$;
    """)
