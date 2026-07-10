#!/usr/bin/env python3
"""
Backfill rule_set snapshots — one-time, idempotent, re-runnable.

RULE-VER-1 introduced rule_set/rule_set_item as a frozen, point-in-time snapshot
mechanism for payroll rate resolution, but snapshots are only ever created
reactively (auto_publish() fires on rule create/version-save). Dates before
RULE-VER-1 shipped never got a snapshot, so historical-dated payroll inputs for
those periods silently fell back to the CURRENT rule set (see rule_evaluator.py
_resolve_rule's current_fallback branch) instead of the rate genuinely in force
at the time.

This script creates the missing snapshots by calling rule_set_service.auto_publish()
— NOT a reimplementation of its query — once per distinct (workspace_id,
effective_from) pair found in payroll_rule. auto_publish() already filters
is_active = TRUE, so a soft-deleted rule version is correctly excluded from every
backfilled snapshot, matching the decision that deleted rules are treated as if
they never existed for historical reconstruction, both here and in all future
snapshots.

Safe to re-run: auto_publish()'s own DELETE+re-INSERT step for an existing,
unlocked rule_set makes re-running a no-op in effect. A rule_set already locked
by a payroll_run (RuleSetLockedError) is skipped, not treated as a failure — a
single locked date never aborts the rest of the backfill.

Usage:
    python backend/scripts/backfill_rule_set_snapshots.py
    python backend/scripts/backfill_rule_set_snapshots.py --workspace-id <uuid>
    python backend/scripts/backfill_rule_set_snapshots.py --dry-run
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from sqlalchemy import text  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.table import Table  # noqa: E402

from backend.infra.db.session import SessionLocal  # noqa: E402
from backend.application.rule_set_service import auto_publish, RuleSetLockedError, SYSTEM_ACTOR  # noqa: E402

console = Console(highlight=False, width=120)


def backfill(workspace_id: str | None = None, dry_run: bool = False) -> None:
    db = SessionLocal()
    try:
        query = """
            SELECT DISTINCT workspace_id, effective_from
            FROM payroll_rule
            WHERE is_active = TRUE
        """
        params: dict = {}
        if workspace_id:
            query += " AND workspace_id = :wid"
            params["wid"] = workspace_id
        query += " ORDER BY workspace_id, effective_from"

        pairs = db.execute(text(query), params).fetchall()

        if not pairs:
            console.print("[yellow]No payroll_rule rows found — nothing to backfill.[/yellow]")
            return

        console.print(f"Found [bold]{len(pairs)}[/bold] distinct (workspace_id, effective_from) pairs.")

        published = 0
        skipped_locked = 0
        failed: list[tuple[str, str, str]] = []

        for ws_id, effective_from in pairs:
            ws_id_str = str(ws_id)
            if dry_run:
                console.print(f"  [dim](dry-run)[/dim] would publish {ws_id_str} @ {effective_from}")
                continue
            try:
                auto_publish(db, ws_id_str, effective_from, created_by_uuid=SYSTEM_ACTOR)
                db.commit()
                published += 1
            except RuleSetLockedError:
                db.rollback()
                skipped_locked += 1
            except Exception as exc:  # noqa: BLE001 — report and continue, don't abort the batch
                db.rollback()
                failed.append((ws_id_str, str(effective_from), str(exc)))

        if dry_run:
            return

        table = Table(title="Backfill summary")
        table.add_column("Metric")
        table.add_column("Count", justify="right")
        table.add_row("Published", str(published))
        table.add_row("Skipped (locked by payroll_run)", str(skipped_locked))
        table.add_row("Failed", str(len(failed)))
        console.print(table)

        if failed:
            console.print("[red]Failures:[/red]")
            for ws_id_str, eff, err in failed:
                console.print(f"  {ws_id_str} @ {eff}: {err}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-id", default=None, help="Scope backfill to a single workspace")
    parser.add_argument("--dry-run", action="store_true", help="List pairs without publishing")
    args = parser.parse_args()

    backfill(workspace_id=args.workspace_id, dry_run=args.dry_run)
