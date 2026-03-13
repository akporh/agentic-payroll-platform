#!/usr/bin/env python3
"""
Developer Seed Tool: Payroll Input Data

Inserts per-period payroll event rows (overtime, allowances, absences, etc.)
into payroll_input for up to 5 ACTIVE employees in a workspace. All rows are
inserted with payroll_run_id = NULL (unclaimed) and source = 'MANUAL'.

Run a payroll run after seeding to claim the rows and see inputs_applied
in the API response.

Usage:
    python scripts/seed_payroll_inputs.py
    python scripts/seed_payroll_inputs.py --workspace-id <uuid>
"""

import sys
import argparse
import uuid
from pathlib import Path

# ── project root on sys.path so backend imports resolve ──────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from sqlalchemy import text  # noqa: E402

from rich.console import Console  # noqa: E402
from rich.table import Table  # noqa: E402
from rich import box  # noqa: E402

from backend.infra.db.session import SessionLocal  # noqa: E402

console = Console()

# ---------------------------------------------------------------------------
# Input definitions: (input_code, input_category, quantity, rate, amount)
# rate=None means it will be looked up or left NULL
# ---------------------------------------------------------------------------
INPUT_ROWS = [
    ("SPECIAL_OVERTIME",    "EARNING",   12,   None,  None),
    ("REGULAR_OVERTIME",    "EARNING",    8,   None,  None),
    ("WEEKEND_ALLOWANCE",   "EARNING",   None, None,  5000),
    ("ABSENCE",             "DEDUCTION",  2,   None,  None),
    ("SUSPENSION",          "DEDUCTION",  1,   None,  None),
    ("ACCIDENT_FREE_BONUS", "EARNING",   None, None,   200),
    ("BONUS",               "EARNING",   None, None,   500),
    ("ADJUSTMENT",          "EARNING",   None, None,  1000),
]


def seed_inputs(session, workspace_id: str | None = None) -> None:
    # ── 1. Resolve workspace ─────────────────────────────────────────────────
    if workspace_id:
        ws_row = session.execute(
            text("SELECT workspace_id, name FROM workspace WHERE workspace_id = :wid"),
            {"wid": workspace_id},
        ).mappings().first()
        if not ws_row:
            console.print(f"[bold red]Workspace {workspace_id} not found.[/bold red]")
            return
    else:
        ws_row = session.execute(
            text("SELECT workspace_id, name FROM workspace ORDER BY created_at LIMIT 1")
        ).mappings().first()
        if not ws_row:
            console.print("[bold red]No workspace found. Run onboarding first.[/bold red]")
            return

    wid = str(ws_row["workspace_id"])
    ws_name = ws_row["name"]
    console.print(f"\n[bold cyan]Seeding payroll inputs for workspace:[/bold cyan] {ws_name}  [dim]({wid})[/dim]\n")

    # ── 2. Load up to 5 ACTIVE employees ─────────────────────────────────────
    emp_rows = session.execute(
        text("""
            SELECT employee_id, full_name, employee_number
            FROM employee
            WHERE workspace_id = :wid
              AND status = 'ACTIVE'
            ORDER BY created_at
            LIMIT 5
        """),
        {"wid": wid},
    ).mappings().fetchall()

    if not emp_rows:
        console.print("[bold red]No ACTIVE employees found in this workspace.[/bold red]")
        return

    console.print(f"Found [bold]{len(emp_rows)}[/bold] ACTIVE employee(s).\n")

    # ── 3. Insert input rows ─────────────────────────────────────────────────
    inserted = []

    for emp in emp_rows:
        emp_id = str(emp["employee_id"])
        emp_name = emp["full_name"] or emp["employee_number"] or emp_id[:8]

        for (code, category, quantity, rate, amount) in INPUT_ROWS:
            row_id = str(uuid.uuid4())
            session.execute(
                text("""
                    INSERT INTO payroll_input (
                        payroll_input_id,
                        workspace_id,
                        payroll_run_id,
                        employee_id,
                        input_code,
                        input_category,
                        quantity,
                        rate,
                        amount,
                        source
                    ) VALUES (
                        :id,
                        :wid,
                        NULL,
                        :emp_id,
                        :code,
                        :category,
                        :quantity,
                        :rate,
                        :amount,
                        'MANUAL'
                    )
                """),
                {
                    "id":       row_id,
                    "wid":      wid,
                    "emp_id":   emp_id,
                    "code":     code,
                    "category": category,
                    "quantity": quantity,
                    "rate":     rate,
                    "amount":   amount,
                },
            )
            inserted.append({
                "employee":  emp_name,
                "code":      code,
                "category":  category,
                "quantity":  str(quantity) if quantity is not None else "—",
                "rate":      str(rate) if rate is not None else "—",
                "amount":    str(amount) if amount is not None else "—",
            })

    session.commit()

    # ── 4. Display results ────────────────────────────────────────────────────
    table = Table(
        title=f"Inserted {len(inserted)} payroll_input rows",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold white",
    )
    table.add_column("Employee", style="cyan")
    table.add_column("Input Code", style="magenta")
    table.add_column("Category", style="dim")
    table.add_column("Qty", justify="right")
    table.add_column("Rate", justify="right")
    table.add_column("Amount", justify="right", style="green")

    for r in inserted:
        cat_color = "green" if r["category"] == "EARNING" else "red"
        table.add_row(
            r["employee"],
            r["code"],
            f"[{cat_color}]{r['category']}[/{cat_color}]",
            r["quantity"],
            r["rate"],
            r["amount"],
        )

    console.print(table)
    console.print()
    console.print(
        "[dim]All rows inserted with payroll_run_id = NULL (unclaimed).[/dim]"
    )
    console.print(
        "[dim]Trigger a payroll run to claim them and see inputs_applied in the response.[/dim]"
    )
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed payroll_input rows for testing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/seed_payroll_inputs.py
  python scripts/seed_payroll_inputs.py --workspace-id <uuid>
        """,
    )
    parser.add_argument(
        "--workspace-id",
        metavar="UUID",
        help="Target a specific workspace (defaults to first workspace found).",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        seed_inputs(session, workspace_id=args.workspace_id)
    finally:
        session.close()


if __name__ == "__main__":
    main()
