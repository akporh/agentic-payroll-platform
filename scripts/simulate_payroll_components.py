#!/usr/bin/env python3
"""
Developer Simulation Tool: Payroll Rule Engine Transparency

Shows step-by-step how salary components are resolved, statutory
deductions computed, and net pay derived — using real database
configuration. Read-only: no writes to the database.

Usage:
    python scripts/simulate_payroll_components.py
    python scripts/simulate_payroll_components.py --trace
    python scripts/simulate_payroll_components.py --workspace-id <uuid>
    python scripts/simulate_payroll_components.py --employee-id <uuid>
"""

import sys
import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# ── project root on sys.path so backend imports resolve ──────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from sqlalchemy import text  # noqa: E402

from rich.console import Console  # noqa: E402
from rich.table import Table  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.text import Text  # noqa: E402
from rich import box  # noqa: E402
from rich.rule import Rule  # noqa: E402
from rich.tree import Tree  # noqa: E402
from rich.padding import Padding  # noqa: E402

from backend.infra.db.session import SessionLocal  # noqa: E402
from backend.infra.db.models.workspace import Workspace  # noqa: E402
from backend.infra.db.models.salary_definition import SalaryDefinition  # noqa: E402
from backend.infra.db.models.payroll_rule import PayrollRule  # noqa: E402
from backend.infra.db.models.component_metadata import (  # noqa: E402
    ComponentMetadata,
    ClientComponentMetadata,
)
from backend.infra.db.models.designation import Designation  # noqa: E402
from backend.infra.db.models.grade import Grade  # noqa: E402
from backend.infra.db.models.pay_cycle import PayCycle  # noqa: E402
from backend.domain.rules.paye import calculate_paye  # noqa: E402
from backend.domain.rules.pension import calculate_pension  # noqa: E402

PENSION_BASE = {"BASIC", "HOUSING", "TRANSPORT"}

console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fmt(amount: Decimal, currency: str = "") -> str:
    """Right-aligned amount string, e.g. '3,000.00' or 'NGN 3,000.00'."""
    s = f"{amount:,.2f}"
    return f"{currency} {s}" if currency else s


def _normalize_components(components_jsonb) -> list[dict]:
    """
    Normalise components_jsonb to [{"code": str, "amount": Decimal}, ...].

    Handles both storage formats emitted by the onboarding pipeline:
      dict  → {"BASIC": 300000, "HOUSING": 100000, ...}
      list  → [{"code": "BASIC", "amount": 300000}, ...]
    """
    if isinstance(components_jsonb, dict):
        return [
            {"code": k, "amount": Decimal(str(v))}
            for k, v in components_jsonb.items()
        ]
    if isinstance(components_jsonb, list):
        out = []
        for item in components_jsonb:
            if isinstance(item, dict):
                code = item.get("code") or item.get("name") or "COMPONENT"
                amt = Decimal(str(item.get("amount", 0)))
            else:
                code = "COMPONENT"
                amt = Decimal(str(item))
            out.append({"code": code, "amount": amt})
        return out
    return []


def _component_meta(
    session,
    code: str,
    workspace_id: str,
    country_code: str,
) -> dict:
    """
    Return the metadata_json dict for a component code.
    Checks client_component_metadata first, then platform component_metadata.
    """
    ccm = (
        session.query(ClientComponentMetadata)
        .filter_by(workspace_id=workspace_id, component_code=code)
        .first()
    )
    if ccm and ccm.metadata_json:
        result = dict(ccm.metadata_json)
        result["_source"] = "client"
        return result

    cm = (
        session.query(ComponentMetadata)
        .filter_by(component_code=code, country_code=country_code, is_active=True)
        .first()
    )
    if cm and cm.metadata_json:
        result = dict(cm.metadata_json)
        result["_source"] = "platform"
        return result

    return {}


def _component_meta_debug(
    session,
    workspace_id: str,
    country_code: str,
    component_codes: list[str],
) -> None:
    """Print METADATA RESOLUTION DEBUG section."""
    console.rule("[bold yellow]METADATA RESOLUTION DEBUG[/bold yellow]", style="yellow")
    console.print()
    console.print(f"  [bold]Workspace ID:[/bold] {workspace_id}")
    console.print()

    # Client rows
    client_rows = (
        session.query(ClientComponentMetadata)
        .filter_by(workspace_id=workspace_id)
        .all()
    )
    console.print(
        f"  [bold]client_component_metadata rows loaded:[/bold] {len(client_rows)}"
    )
    if client_rows:
        for row in client_rows:
            console.print(f"    • {row.component_code}")
    else:
        console.print("    [dim](none)[/dim]")
    console.print()

    # Platform rows relevant to these components
    platform_rows = (
        session.query(ComponentMetadata)
        .filter(
            ComponentMetadata.country_code == country_code,
            ComponentMetadata.is_active.is_(True),
        )
        .all()
    )
    console.print(
        f"  [bold]platform component_metadata rows loaded[/bold]"
        f" [dim](country={country_code}, is_active=True):[/dim] {len(platform_rows)}"
    )
    if platform_rows:
        for row in platform_rows:
            console.print(f"    • {row.component_code}")
    else:
        console.print("    [dim](none)[/dim]")
    console.print()

    # Per-component lookup trace
    console.print("  [bold]COMPONENT METADATA LOOKUP[/bold]")
    console.print()
    client_codes = {r.component_code for r in client_rows}
    platform_codes = {r.component_code for r in platform_rows}
    for code in component_codes:
        found_client = code in client_codes
        found_platform = code in platform_codes
        status = (
            "[green]client[/green]" if found_client
            else ("[dim]platform[/dim]" if found_platform else "[red]MISSING[/red]")
        )
        console.print(f"  [bold cyan]{code}[/bold cyan]")
        console.print(
            f"    client_metadata_found : "
            f"{'[green]true[/green]' if found_client else '[dim]false[/dim]'}"
        )
        console.print(
            f"    platform_metadata_found: "
            f"{'[green]true[/green]' if found_platform else '[dim]false[/dim]'}"
        )
        console.print(f"    resolved_source       : {status}")

        if found_client:
            row = next(r for r in client_rows if r.component_code == code)
            console.print(f"    metadata              : {row.metadata_json}")
        elif found_platform:
            row = next(r for r in platform_rows if r.component_code == code)
            console.print(f"    metadata              : {row.metadata_json}")
        else:
            console.print(
                "    [red]⚠ No metadata in client_component_metadata or"
                " component_metadata — category will be inferred[/red]"
            )
        console.print()

    console.rule(style="dim yellow")
    console.print()


def _category(meta: dict) -> str:
    return meta.get("financial_role", {}).get("category", "earning")


def _category_display(meta: dict) -> tuple[str, bool]:
    """Return (category_string, inferred_bool)."""
    if not meta:
        return "earning", True
    cat = meta.get("financial_role", {}).get("category")
    if cat is None:
        return "earning", True
    return cat, False


# ─────────────────────────────────────────────────────────────────────────────
# Trace graph
# ─────────────────────────────────────────────────────────────────────────────

def _print_trace(
    components: list[dict],
    statutory_names: list[str],
    paye_amount: Decimal,
    pension_employee: Decimal,
    net_pay: Decimal,
    currency: str,
):
    console.print()
    console.rule("[bold yellow]EXECUTION DEPENDENCY GRAPH[/bold yellow]", style="yellow")
    console.print()

    tree = Tree(
        "[bold white]BASE_SALARY (salary_definition)[/bold white]",
        guide_style="dim white",
    )

    earning_branch = tree.add("[green]EARNINGS[/green]")
    for c in components:
        meta = c.get("_meta", {})
        cat = _category(meta)
        color = "green" if cat == "earning" else "yellow"
        earning_branch.add(
            f"[{color}]{c['code']}[/{color}]  "
            f"[dim]{_fmt(c['amount'], currency)}[/dim]"
        )

    gross = sum(c["amount"] for c in components)
    gross_node = tree.add(
        f"[bold green]GROSS_PAY  [dim]{_fmt(gross, currency)}[/dim][/bold green]"
    )

    if statutory_names or paye_amount > 0 or pension_employee > 0:
        deduct_branch = gross_node.add("[red]DEDUCTIONS[/red]")
        if pension_employee > 0:
            deduct_branch.add(
                f"[red]PENSION_EMPLOYEE (PRA 2014)[/red]  "
                f"[dim]- {_fmt(pension_employee, currency)}[/dim]"
            )
        if paye_amount > 0:
            deduct_branch.add(
                f"[red]PAYE (tax bands)[/red]  "
                f"[dim]- {_fmt(paye_amount, currency)}[/dim]"
            )
        for name in statutory_names:
            deduct_branch.add(f"[red]{name}[/red]")

    gross_node.add(
        f"[bold cyan]NET_PAY  [dim]{_fmt(net_pay, currency)}[/dim][/bold cyan]"
    )

    console.print(Padding(tree, (0, 4)))
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Main simulation
# ─────────────────────────────────────────────────────────────────────────────

def simulate_payroll(
    session,
    employee_id: str | None = None,
    workspace_id: str | None = None,
    trace: bool = False,
):
    # ── 1. Employee ──────────────────────────────────────────────────────────
    if employee_id:
        row = session.execute(
            text("SELECT * FROM employee WHERE employee_id = :eid"),
            {"eid": employee_id},
        ).mappings().first()
    elif workspace_id:
        row = session.execute(
            text("SELECT * FROM employee WHERE workspace_id = :wid LIMIT 1"),
            {"wid": workspace_id},
        ).mappings().first()
    else:
        row = session.execute(
            text("SELECT * FROM employee ORDER BY created_at LIMIT 1")
        ).mappings().first()

    if not row:
        console.print("[bold red]No employee found. Load onboarding data first.[/bold red]")
        return

    emp = dict(row)
    emp_workspace_id = str(emp["workspace_id"])

    # ── 2. Workspace ─────────────────────────────────────────────────────────
    workspace = (
        session.query(Workspace)
        .filter_by(workspace_id=emp_workspace_id)
        .first()
    )
    if not workspace:
        console.print(f"[bold red]Workspace {emp_workspace_id} not found.[/bold red]")
        return

    currency = workspace.base_currency or ""
    country_code = workspace.country_code or "NG"

    # ── 3. Employee contract → salary definition, designation, grade ─────────
    contract_row = session.execute(
        text("""
            SELECT ec.*,
                   d.designation_code,
                   g.grade_code
            FROM   employee_contract ec
            LEFT   JOIN designation d ON d.designation_id = ec.designation_id
            LEFT   JOIN grade       g ON g.grade_id       = ec.grade_id
            WHERE  ec.employee_id = :eid
              AND  (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
            ORDER  BY ec.start_date DESC
            LIMIT  1
        """),
        {"eid": str(emp["employee_id"])},
    ).mappings().first()

    contract = dict(contract_row) if contract_row else {}
    designation_code = contract.get("designation_code") or "—"
    grade_code = contract.get("grade_code") or "—"

    salary_def = None
    if contract.get("salary_definition_id"):
        salary_def = (
            session.query(SalaryDefinition)
            .filter_by(salary_definition_id=contract["salary_definition_id"])
            .first()
        )

    if not salary_def:
        salary_def = (
            session.query(SalaryDefinition)
            .filter_by(workspace_id=emp_workspace_id)
            .first()
        )

    # ── 4. Pay cycle ─────────────────────────────────────────────────────────
    pay_cycle = (
        session.query(PayCycle)
        .filter_by(workspace_id=emp_workspace_id, is_active=True)
        .first()
    )

    # ── 5. Payroll rules ─────────────────────────────────────────────────────
    payroll_rules = (
        session.query(PayrollRule)
        .filter_by(workspace_id=emp_workspace_id, is_active=True)
        .all()
    )

    # ── 6. Statutory rule + tax bands ────────────────────────────────────────
    if workspace.statutory_rule_id:
        statutory_row = session.execute(
            text("SELECT * FROM statutory_rule WHERE statutory_rule_id = :sid"),
            {"sid": str(workspace.statutory_rule_id)},
        ).mappings().first()
    else:
        statutory_row = None
        console.print(
            "[yellow]WARNING: workspace has no statutory_rule_id set. "
            "PAYE will not be calculated.[/yellow]"
        )

    statutory_rule = dict(statutory_row) if statutory_row else {}

    # Extract pension + relief config from rules_jsonb
    rules_jsonb = statutory_rule.get("rules_jsonb") or {}
    pension_cfg = rules_jsonb.get("pension", {}) if isinstance(rules_jsonb, dict) else {}
    rent_relief_cfg = (
        rules_jsonb.get("reliefs", {}).get("rent_relief", {})
        if isinstance(rules_jsonb, dict)
        else {}
    )

    tax_bands: list[dict] = []
    if statutory_rule.get("statutory_rule_id"):
        bands = session.execute(
            text(
                "SELECT * FROM tax_band "
                "WHERE statutory_rule_id = :sid ORDER BY lower_limit"
            ),
            {"sid": str(statutory_rule["statutory_rule_id"])},
        ).mappings().all()
        tax_bands = [dict(b) for b in bands]
        if not tax_bands:
            console.print(
                f"[yellow]WARNING: statutory rule "
                f"(state={statutory_rule.get('state')}, "
                f"v{statutory_rule.get('version')}) has no tax bands. "
                f"PAYE will not be calculated.[/yellow]"
            )

    # ── 7. Normalise components ───────────────────────────────────────────────
    raw_components = _normalize_components(
        salary_def.components_jsonb if salary_def else {}
    )

    # Attach metadata to each component (also records _source: "client"/"platform"/"")
    for c in raw_components:
        c["_meta"] = _component_meta(
            session, c["code"], emp_workspace_id, country_code
        )

    earnings = [c for c in raw_components if _category(c["_meta"]) == "earning"]
    other_components = [c for c in raw_components if _category(c["_meta"]) != "earning"]
    display_components = earnings or raw_components  # fallback if no meta tags

    # ─────────────────────────────────────────────────────────────────────────
    # DEBUG: metadata resolution (always shown so mismatches are visible)
    # ─────────────────────────────────────────────────────────────────────────
    _component_meta_debug(
        session,
        emp_workspace_id,
        country_code,
        [c["code"] for c in raw_components],
    )

    # ─────────────────────────────────────────────────────────────────────────
    # OUTPUT
    # ─────────────────────────────────────────────────────────────────────────
    console.print()
    console.rule("[bold cyan]PAYROLL SIMULATION ENGINE[/bold cyan]", style="cyan")
    console.print()

    # ── Employee panel ────────────────────────────────────────────────────────
    biodata = emp.get("personal_details_encrypted") or {}
    if isinstance(biodata, str):
        import json as _json
        try:
            biodata = _json.loads(biodata)
        except Exception:
            biodata = {}

    full_name = emp.get("full_name") or biodata.get("FULL_NAME") or "Unknown"

    info_lines = [
        f"[bold]Employee   :[/bold] {full_name}",
        f"[bold]Number     :[/bold] {emp.get('employee_number') or '—'}",
        f"[bold]Designation:[/bold] {designation_code}",
        f"[bold]Grade      :[/bold] {grade_code}",
        f"[bold]Workspace  :[/bold] {workspace.name}  "
        f"[dim]({workspace.country_code}  {workspace.base_currency})[/dim]",
        f"[bold]Status     :[/bold] {emp.get('status') or workspace.status or '—'}",
    ]
    if pay_cycle:
        info_lines.append(
            f"[bold]Pay Cycle  :[/bold] {pay_cycle.frequency}  "
            f"[dim](run day {pay_cycle.run_day}, "
            f"payment day {pay_cycle.payment_day})[/dim]"
        )

    console.print(
        Panel(
            "\n".join(info_lines),
            title="[bold white]EMPLOYEE[/bold white]",
            border_style="bright_blue",
            expand=False,
            padding=(1, 3),
        )
    )
    console.print()

    # ── Metadata notice panel (after employee, before salary structure) ───────
    missing_meta_codes = [
        c["code"] for c in raw_components if not c.get("_meta")
    ]
    if missing_meta_codes:
        bullet_lines = "\n".join(f"  • {code}" for code in missing_meta_codes)
        notice_text = (
            'The following components have no metadata entry. Category\n'
            'has been inferred as "earning":\n'
            f'{bullet_lines}\n\n'
            'To resolve: seed rows into client_component_metadata for\n'
            f'workspace {emp_workspace_id}'
        )
        console.print(
            Panel(
                notice_text,
                title="[bold yellow]METADATA NOTICE[/bold yellow]",
                border_style="yellow",
                expand=False,
                padding=(0, 2),
            )
        )
        console.print()

    # ── Salary structure panel ────────────────────────────────────────────────
    if salary_def:
        sal_table = Table(
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style="bold white",
            expand=False,
        )
        sal_table.add_column("COMPONENT", style="cyan")
        sal_table.add_column("AMOUNT", justify="right", style="green")
        sal_table.add_column("CATEGORY", style="dim")

        for c in raw_components:
            cat, inferred = _category_display(c["_meta"])
            color = "green" if cat == "earning" else ("red" if cat == "deduction" else "dim")
            if inferred:
                cat_cell = f"[dim]{cat} (inferred)[/dim]"
            else:
                cat_cell = f"[{color}]{cat}[/{color}]"
            sal_table.add_row(
                c["code"],
                _fmt(c["amount"], currency),
                cat_cell,
            )

        console.print(
            Panel(
                sal_table,
                title=f"[bold white]SALARY STRUCTURE[/bold white]"
                      f"  [dim]{salary_def.code or salary_def.name or ''}[/dim]",
                border_style="green",
                expand=False,
            )
        )
    else:
        console.print(
            Panel(
                "[yellow]No salary definition linked to this employee.[/yellow]",
                title="SALARY STRUCTURE",
                border_style="yellow",
            )
        )

    console.print()

    # ── Step-by-step component resolution ────────────────────────────────────
    console.rule("[bold green]COMPONENT RESOLUTION[/bold green]", style="green")
    console.print()

    gross = Decimal("0")
    step_n = 0

    for c in raw_components:
        step_n += 1
        amt = c["amount"]
        gross += amt
        meta = c["_meta"]
        cat = _category(meta)
        color = "green" if cat == "earning" else ("red" if cat == "deduction" else "yellow")
        is_statutory = meta.get("legal_role", {}).get("is_statutory", False)

        header = Text()
        header.append(f"[STEP {step_n}]  ", style="bold dim")
        header.append(c["code"], style=f"bold {color}")
        if is_statutory:
            header.append("  [STATUTORY]", style="dim red")

        console.print(header)
        meta_source = meta.get("_source", "") if meta else ""
        if not meta:
            console.print(f"  category      : [dim]{cat} (inferred)[/dim]")
            console.print(
                "[dim]  ⚠  no metadata found in component_metadata "
                "or client_component_metadata[/dim]"
            )
        else:
            source_label = (
                "  [dim](source: client_component_metadata)[/dim]"
                if meta_source == "client"
                else "  [dim](source: platform component_metadata)[/dim]"
                if meta_source == "platform"
                else ""
            )
            console.print(f"  category      : [{color}]{cat}[/{color}]{source_label}")

        if meta:
            fin_role = meta.get("financial_role", {})
            if fin_role.get("affects_gross") is not None:
                console.print(
                    f"  affects_gross : {'yes' if fin_role['affects_gross'] else 'no'}"
                )
            net_effect = fin_role.get("net_effect")
            if net_effect:
                console.print(f"  net_effect    : {net_effect}")

        console.print(f"  amount        : [bold]{_fmt(amt, currency)}[/bold]")
        console.print(f"  running gross : {_fmt(gross, currency)}")
        console.print()

    # ── Pension contributions ──────────────────────────────────────────────────
    pension_employee = Decimal("0")
    pension_employer = Decimal("0")

    console.rule("[bold magenta]PENSION CONTRIBUTIONS (PRA 2014)[/bold magenta]", style="magenta")
    console.print()

    if pension_cfg:
        pensionable_base = sum(
            c["amount"] for c in raw_components if c["code"] in PENSION_BASE
        )
        emp_rate = Decimal(str(pension_cfg.get("employee_rate", 0)))
        er_rate = Decimal(str(pension_cfg.get("employer_rate", 0)))
        pension_employee, pension_employer = calculate_pension(pensionable_base, emp_rate, er_rate)

        pensionable_codes = [c["code"] for c in raw_components if c["code"] in PENSION_BASE]
        codes_str = " + ".join(pensionable_codes) if pensionable_codes else "none found"

        console.print(
            f"  [bold]Pensionable Base[/bold] : "
            f"[bold]{_fmt(pensionable_base, currency)}[/bold]"
            f"  [dim]({codes_str})[/dim]"
        )
        console.print(
            f"  [bold]Employee {float(emp_rate)*100:.1f}%  [/bold] : "
            f"[bold magenta]{_fmt(pension_employee, currency)}[/bold magenta]"
            f"  [dim][DEDUCTION — reduces net pay + tax base][/dim]"
        )
        console.print(
            f"  [bold]Employer {float(er_rate)*100:.1f}%  [/bold] : "
            f"[bold dim]{_fmt(pension_employer, currency)}[/bold dim]"
            f"  [dim][EMPLOYER COST — not deducted from employee][/dim]"
        )
    else:
        console.print(
            "[dim]  ⚠  No pension config in statutory_rule.rules_jsonb[/dim]"
        )

    console.print()

    # ── Payroll rules ─────────────────────────────────────────────────────────
    if payroll_rules:
        console.rule("[bold yellow]PAYROLL RULES[/bold yellow]", style="yellow")
        console.print()

        for i, rule in enumerate(payroll_rules, 1):
            defn = rule.rule_definition_json or {}
            rule_name = rule.rule_name or f"RULE_{i}"
            rule_type = rule.rule_type or "unknown"

            header = Text()
            header.append(f"[RULE {i}]  ", style="bold dim")
            header.append(rule_name.upper(), style="bold yellow")
            console.print(header)

            if rule_type == "unit_multiplier":
                rate_val = defn.get("rate") or defn.get("rate_per_unit", "?")
                unit = defn.get("unit", "unit")
                input_field = defn.get("input_field") or defn.get("requires") or "?"
                console.print(f"  method        : unit_multiplier  (rate={rate_val}/{unit})")
                console.print(f"  requires      : {input_field}  [dim][employee event data][/dim]")
                console.print(
                    "  status        : [bold red]NOT APPLIED[/bold red] — "
                    "no employee event data supplied for this run"
                )
                console.print("  impact        : [dim]NGN 0.00[/dim]")

            elif rule_type == "daily_rate_deduction":
                rate_val = defn.get("rate") or defn.get("daily_rate", "?")
                input_field = defn.get("input_field") or defn.get("requires") or "?"
                console.print(f"  method        : daily_rate_deduction  (rate={rate_val}/day)")
                console.print(f"  requires      : {input_field}  [dim][employee event data][/dim]")
                console.print(
                    "  status        : [bold red]NOT APPLIED[/bold red] — "
                    "no employee event data supplied for this run"
                )
                console.print("  impact        : [dim]NGN 0.00[/dim]")

            elif rule_type == "fixed_amount":
                amount_val = defn.get("amount", "?")
                conditions = defn.get("conditions") or defn.get("condition") or {}
                console.print(f"  method        : fixed_amount  ({currency} {amount_val})")
                if conditions:
                    if isinstance(conditions, dict):
                        cond_parts = [f"{k}={v} ?" for k, v in conditions.items()]
                        console.print(f"  conditions    : {' | '.join(cond_parts)}")
                    else:
                        console.print(f"  conditions    : {conditions}")
                console.print(
                    "  status        : [bold red]NOT APPLIED[/bold red] — "
                    "condition data not available for this simulation"
                )
                console.print("  impact        : [dim]NGN 0.00[/dim]")

            else:
                # Generic fallback for any other rule type
                input_field = defn.get("input_field") or defn.get("requires") or "?"
                console.print(f"  method        : {rule_type}")
                if input_field and input_field != "?":
                    console.print(f"  requires      : {input_field}  [dim][employee event data][/dim]")
                console.print(
                    "  status        : [bold red]NOT APPLIED[/bold red] — "
                    "no employee event data supplied for this run"
                )
                console.print("  impact        : [dim]NGN 0.00[/dim]")

            console.print()

        total_rules = len(payroll_rules)
        console.print(
            f"[dim]{total_rules} rules checked — 0 applied "
            "(no employee event data in simulation context)[/dim]"
        )
        console.print()

    # ── PAYE / Tax calculation ─────────────────────────────────────────────────
    # Nigeria PAYE is assessed on annual income. Annualize the monthly gross,
    # apply pension + rent relief deductions, then compute tax on taxable income.
    paye_amount = Decimal("0")

    if tax_bands:
        console.rule("[bold red]TAX CALCULATION (PAYE)[/bold red]", style="red")
        console.print()

        annual_gross = gross * 12
        annual_pension_employee = pension_employee * 12

        # Rent relief
        annual_rent_relief = Decimal("0")
        if rent_relief_cfg.get("enabled"):
            cap = Decimal(str(rent_relief_cfg.get("cap", 0)))
            rate_rr = Decimal(str(rent_relief_cfg.get("rate", 0)))
            annual_rent_relief = min(annual_gross * rate_rr, cap)

        # CRA is abolished under Nigeria Tax Act 2025
        deductible_relief = annual_pension_employee + annual_rent_relief
        annual_taxable_income = annual_gross - deductible_relief

        console.print(f"  [bold]Monthly Gross [/bold] : {_fmt(gross, currency)}")
        console.print(f"  [bold]Annual Gross  [/bold] : {_fmt(annual_gross, currency)}  [dim](× 12)[/dim]")
        console.print(
            f"  [bold]Tax Method    [/bold] : "
            f"{statutory_rule.get('tax_method', 'CUMULATIVE')}"
        )
        console.print(
            f"  [bold]Statutory Rule[/bold] : "
            f"state={statutory_rule.get('state')}  "
            f"v{statutory_rule.get('version')}"
        )
        console.print()

        # Relief section
        console.print("  [bold]Deductible Reliefs[/bold]")
        console.print(
            f"    Annual Pension Employee : "
            f"[red]−{_fmt(annual_pension_employee, currency)}[/red]"
        )
        if rent_relief_cfg.get("enabled"):
            rr_rate_pct = float(rent_relief_cfg.get("rate", 0)) * 100
            console.print(
                f"    Annual Rent Relief      : "
                f"[red]−{_fmt(annual_rent_relief, currency)}[/red]"
                f"  [dim]({rr_rate_pct:.0f}% of gross, capped)[/dim]"
            )
        else:
            console.print("    Annual Rent Relief      : [dim]n/a (not enabled)[/dim]")
        console.print("    CRA                     : [dim]n/a  (abolished under Nigeria Tax Act 2025)[/dim]")
        console.print("  " + "─" * 50)
        console.print(
            f"  [bold]Annual Taxable Income   [/bold] : "
            f"[bold]{_fmt(annual_taxable_income, currency)}[/bold]"
        )
        console.print()

        band_table = Table(
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style="bold white",
            expand=False,
        )
        band_table.add_column("LOWER LIMIT", justify="right", style="dim")
        band_table.add_column("UPPER LIMIT", justify="right", style="dim")
        band_table.add_column("RATE", justify="right", style="yellow")
        band_table.add_column("TAXABLE IN BAND", justify="right")
        band_table.add_column("TAX IN BAND", justify="right", style="red")

        sorted_bands = sorted(tax_bands, key=lambda b: Decimal(str(b["lower_limit"])))
        for band in sorted_bands:
            lower = Decimal(str(band["lower_limit"]))
            upper = (
                Decimal(str(band["upper_limit"]))
                if band.get("upper_limit") is not None
                else None
            )
            rate = Decimal(str(band["rate"]))

            if annual_taxable_income <= lower:
                band_table.add_row(
                    _fmt(lower),
                    _fmt(upper) if upper else "∞",
                    f"{float(rate)*100:.1f}%",
                    "—",
                    "—",
                )
                continue

            in_band = (
                min(annual_taxable_income, upper) - lower
                if upper is not None
                else annual_taxable_income - lower
            )
            in_band = max(in_band, Decimal("0"))
            tax_here = (in_band * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            upper_display = _fmt(upper) if upper is not None else "∞"
            band_table.add_row(
                _fmt(lower),
                upper_display,
                f"{float(rate)*100:.1f}%",
                _fmt(in_band, currency),
                f"[bold red]{_fmt(tax_here, currency)}[/bold red]",
            )

        annual_paye = calculate_paye(
            annual_taxable_income,
            [
                {
                    "lower_limit": float(b["lower_limit"]),
                    "upper_limit": float(b["upper_limit"])
                    if b.get("upper_limit") is not None
                    else None,
                    "rate": float(b["rate"]),
                }
                for b in tax_bands
            ],
        )
        paye_amount = (annual_paye / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        console.print(band_table)
        console.print()
        console.print(
            f"  [bold]ANNUAL PAYE [/bold] = [bold red]{_fmt(annual_paye, currency)}[/bold red]"
        )
        console.print(
            f"  [bold]MONTHLY PAYE[/bold] = [bold red]{_fmt(paye_amount, currency)}[/bold red]"
            f"  [dim](÷ 12)[/dim]"
        )
        console.print()

    # statutory_names is used only for the trace graph — PENSION is now handled
    # explicitly, so we leave this empty (rules_jsonb keys are config, not deductions)
    statutory_names: list[str] = []

    # ── Final summary ─────────────────────────────────────────────────────────
    console.rule("[bold cyan]PAYROLL SUMMARY[/bold cyan]", style="cyan")
    console.print()

    earnings_total = sum(
        c["amount"]
        for c in raw_components
        if _category(c["_meta"]) == "earning"
    )
    if earnings_total == 0:
        earnings_total = gross  # treat all as earnings if no category tagged

    total_deductions = (pension_employee + paye_amount).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    net_pay = (gross - total_deductions).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    summary = Table(
        box=box.SIMPLE,
        show_header=False,
        expand=False,
        padding=(0, 2),
    )
    summary.add_column("LABEL", style="bold", min_width=32)
    summary.add_column("AMOUNT", justify="right", min_width=18)

    # Earnings section
    summary.add_row("[bold green]EARNINGS[/bold green]", "")
    for c in raw_components:
        cat = _category(c["_meta"])
        if cat in ("earning", "") or not c["_meta"]:
            summary.add_row(f"  {c['code']}", _fmt(c["amount"], currency))

    summary.add_row(
        "[bold green]Total Earnings[/bold green]",
        f"[bold green]{_fmt(earnings_total, currency)}[/bold green]",
    )
    summary.add_row("", "")

    # Deductions section
    if total_deductions > 0 or other_components:
        summary.add_row("[bold red]DEDUCTIONS[/bold red]", "")
        if pension_employee > 0:
            emp_rate_pct = float(pension_cfg.get("employee_rate", 0)) * 100 if pension_cfg else 0
            summary.add_row(
                f"  Pension (employee {emp_rate_pct:.1f}%)",
                _fmt(pension_employee, currency),
            )
        if paye_amount > 0:
            summary.add_row("  PAYE (income tax)", _fmt(paye_amount, currency))
        for c in other_components:
            summary.add_row(f"  {c['code']}", _fmt(c["amount"], currency))
        summary.add_row(
            "[bold red]Total Deductions[/bold red]",
            f"[bold red]{_fmt(total_deductions, currency)}[/bold red]",
        )
        summary.add_row("", "")

    summary.add_row(
        "[bold cyan]NET PAY[/bold cyan]",
        f"[bold cyan]{_fmt(net_pay, currency)}[/bold cyan]",
    )

    console.print(
        Panel(
            summary,
            title="[bold white]PAYROLL SUMMARY[/bold white]",
            border_style="cyan",
            expand=False,
        )
    )
    console.print()

    # ── Employer costs (shown separately — not deducted from employee) ─────────
    if pension_employer > 0:
        er_rate_pct = float(pension_cfg.get("employer_rate", 0)) * 100 if pension_cfg else 0
        employer_costs = Table(
            box=box.SIMPLE,
            show_header=False,
            expand=False,
            padding=(0, 2),
        )
        employer_costs.add_column("LABEL", style="bold", min_width=32)
        employer_costs.add_column("AMOUNT", justify="right", min_width=18)
        employer_costs.add_row(
            "[bold dim]EMPLOYER COSTS (not deducted from employee)[/bold dim]", ""
        )
        employer_costs.add_row(
            f"  Pension (employer {er_rate_pct:.1f}%)",
            f"[dim]{_fmt(pension_employer, currency)}[/dim]",
        )
        console.print(
            Panel(
                employer_costs,
                title="[bold dim]EMPLOYER COSTS[/bold dim]",
                border_style="dim",
                expand=False,
            )
        )
        console.print()

    # ── Trace graph ────────────────────────────────────────────────────────────
    if trace:
        _print_trace(raw_components, statutory_names, paye_amount, pension_employee, net_pay, currency)

    console.rule(style="dim")
    console.print(
        "[dim]Simulation complete — no database writes were made.[/dim]",
        justify="center",
    )
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate a payroll run for one employee (read-only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/simulate_payroll_components.py
  python scripts/simulate_payroll_components.py --trace
  python scripts/simulate_payroll_components.py --workspace-id <uuid>
  python scripts/simulate_payroll_components.py --employee-id <uuid>
        """,
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Print the component execution dependency graph after the simulation.",
    )
    parser.add_argument(
        "--workspace-id",
        metavar="UUID",
        help="Scope simulation to a specific workspace (picks first employee in it).",
    )
    parser.add_argument(
        "--employee-id",
        metavar="UUID",
        help="Run simulation for a specific employee.",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        simulate_payroll(
            session,
            employee_id=args.employee_id,
            workspace_id=args.workspace_id,
            trace=args.trace,
        )
    finally:
        session.close()


if __name__ == "__main__":
    main()
