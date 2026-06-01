"""Shared JSON serialisation utilities for JSONB-compatible payloads.

Decimal must serialise as a JSON *number* (float), not a string.
String serialisation breaks `val::text::numeric` casts in PostgreSQL JSONB queries.

See: feedback_jsonb_decimal_serialization.md
"""

import json
from decimal import Decimal


def _jsonb_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


def sanitize_jsonb(payload: dict | list | None) -> dict | list:
    """Round-trip a payload through JSON to coerce all values to JSONB-safe types.

    Decimals become floats (preserving numeric queryability).
    Other non-serialisable types fall back to str().
    Returns {} for None input.
    """
    if payload is None:
        return {}
    return json.loads(json.dumps(payload, default=_jsonb_default))
