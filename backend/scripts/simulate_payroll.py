#!/usr/bin/env python3
"""
Sequential Payroll Simulator — developer tool.

Runs the real run_sequential_payroll() engine for a single employee and
prints the full execution trace and results in a structured, sourced layout.
Read-only: no database writes.

Usage:
    python backend/scripts/simulate_payroll.py
    python backend/scripts/simulate_payroll.py --employee-number EMP001
    python backend/scripts/simulate_payroll.py --workspace-id <uuid> --employee-number EMP001
"""

import sys
import argparse
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from sqlalchemy import text  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.panel import Panel  # noqa: E402

from backend.infra.db.session import SessionLocal  # noqa: E402
from backend.domain.payroll.sequential_executor import (  # noqa: E402
    build_runtime_component_registry,
    run_sequential_payroll,
)
from backend.domain.payroll.rule_evaluator import apply_payroll_rules  # noqa: E402
from backend.domain.payroll.period_context import build_period_context  # noqa: E402

console = Console(highlight=False, width=120)
I = "     "  # indent


def _fmt(value, currency: str = "") -> str:
    try:
        d = Decimal(str(value))
    except Exception:
        return str(value)
    s = f"{d:,.2f}"
    return f"{currency} {s}" if currency else s


def _pct(r) -> str:
    return f"{Decimal(str(r)) * 100:.1f}%"


# ── Data loaders ───────────────────────────────────────────────────────────────

def _load_employee(db, employee_id, employee_number, workspace_id=None):
    if employee_id:
        row = db.execute(
            text("SELECT * FROM employee WHERE employee_id = :eid"),
            {"eid": employee_id},
        ).mappings().first()
    elif employee_number and workspace_id:
        row = db.execute(
            text("SELECT * FROM employee WHERE employee_number = :num AND workspace_id = :wid AND status = 'ACTIVE' LIMIT 1"),
            {"num": employee_number, "wid": workspace_id},
        ).mappings().first()
    elif employee_number:
        row = db.execute(
            text("SELECT * FROM employee WHERE employee_number = :num AND status = 'ACTIVE' LIMIT 1"),
            {"num": employee_number},
        ).mappings().first()
    else:
        where  = "WHERE status = 'ACTIVE'" + (" AND workspace_id = :wid" if workspace_id else "")
        params = {"wid": workspace_id} if workspace_id else {}
        row = db.execute(
            text(f"SELECT * FROM employee {where} ORDER BY created_at LIMIT 1"), params
        ).mappings().first()
    if not row:
        console.print("[bold red]No matching employee found.[/bold red]")
        sys.exit(1)
    return dict(row)


def _load_workspace(db, workspace_id):
    row = db.execute(
        text("SELECT * FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id}
    ).mappings().first()
    if not row:
        console.print(f"[bold red]Workspace {workspace_id} not found.[/bold red]")
        sys.exit(1)
    return dict(row)


def _load_contract_details(db, employee_id):
    row = db.execute(text("""
        SELECT d.designation_code, g.grade_code, ec.start_date
        FROM   employee_contract ec
        LEFT JOIN designation d ON d.designation_id = ec.designation_id
        LEFT JOIN grade       g ON g.grade_id       = ec.grade_id
        WHERE  ec.employee_id = :eid
          AND  (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
        ORDER  BY ec.start_date DESC
        LIMIT  1
    """), {"eid": employee_id}).mappings().first()
    return dict(row) if row else {}


def _load_pay_cycle(db, workspace_id):
    row = db.execute(text("""
        SELECT frequency, run_day, cutoff_day, payment_day, definition_json
        FROM   pay_cycle
        WHERE  workspace_id = :wid AND is_active = TRUE
        LIMIT  1
    """), {"wid": workspace_id}).mappings().first()
    return dict(row) if row else {}


def _load_salary_components(db, employee_id):
    row = db.execute(text("""
        SELECT sd.salary_definition_id, sd.code AS sd_code, sd.components_jsonb
        FROM   employee e
        JOIN   employee_contract ec ON ec.employee_id = e.employee_id
               AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
        JOIN   salary_definition sd ON sd.salary_definition_id = ec.salary_definition_id
        WHERE  e.employee_id = :eid
        ORDER  BY ec.start_date DESC
        LIMIT  1
    """), {"eid": employee_id}).mappings().first()
    if not row:
        console.print(f"[bold red]No active contract/salary definition for {employee_id}.[/bold red]")
        sys.exit(1)
    sal_def = dict(row)
    raw = sal_def["components_jsonb"] or {}
    components = {
        code: Decimal(str(v["amount"] if isinstance(v, dict) else v))
        for code, v in raw.items()
    }
    return sal_def, components


def _load_statutory_rule(db, workspace_id):
    from datetime import date as _date
    row = db.execute(text("""
        SELECT sr.*
        FROM   statutory_rule sr
        JOIN   workspace w ON sr.country_code = w.country_code
        WHERE  w.workspace_id = :wid
          AND  sr.effective_from <= :today
        ORDER  BY sr.effective_from DESC, sr.version DESC
        LIMIT  1
    """), {"wid": workspace_id, "today": str(_date.today())}).mappings().first()
    if not row:
        console.print("[bold red]No statutory rule found for this workspace's country.[/bold red]")
        sys.exit(1)
    sr = dict(row)
    pension_cfg = (sr.get("rules_jsonb") or {}).get("pension")
    if not pension_cfg or "employee_rate" not in pension_cfg or "employer_rate" not in pension_cfg:
        console.print("[bold red]Statutory rule is missing pension rates. Run the pension rates migration.[/bold red]")
        sys.exit(1)
    pension_employee_rate = Decimal(str(pension_cfg["employee_rate"]))
    pension_employer_rate = Decimal(str(pension_cfg["employer_rate"]))
    return sr, pension_employee_rate, pension_employer_rate


def _load_tax_bands(db, statutory_rule_id):
    rows = db.execute(text("""
        SELECT lower_limit, upper_limit, rate
        FROM   tax_band WHERE statutory_rule_id = :sr_id ORDER BY lower_limit
    """), {"sr_id": statutory_rule_id}).fetchall()
    return [
        {"lower_limit": float(r[0]), "upper_limit": float(r[1]) if r[1] is not None else None, "rate": float(r[2])}
        for r in rows
    ]


def _load_component_metadata(db, country_code):
    rows = db.execute(text("""
        SELECT component_code, component_class, calculation_method,
               execution_priority, is_active, metadata_json
        FROM   component_metadata
        WHERE  country_code = :cc AND is_active = TRUE
        ORDER  BY execution_priority NULLS LAST
    """), {"cc": country_code}).mappings().all()
    return [dict(r) for r in rows]


def _load_client_overrides(db, workspace_id):
    rows = db.execute(text("""
        SELECT component_code, overrides_json
        FROM   client_component_metadata
        WHERE  workspace_id = :wid
    """), {"wid": workspace_id}).fetchall()
    return {r[0]: r[1] for r in rows}


def _load_payroll_rules(db, workspace_id):
    from datetime import date as _date
    today = str(_date.today())
    rs_row = db.execute(text("""
        SELECT rule_set_id FROM rule_set
        WHERE  workspace_id  = :wid
          AND  effective_from <= :today
        ORDER  BY effective_from DESC, created_at DESC
        LIMIT  1
    """), {"wid": workspace_id, "today": today}).fetchone()

    if rs_row:
        rows = db.execute(text("""
            SELECT rule_name, rule_definition_json, rule_type
            FROM   rule_set_item
            WHERE  rule_set_id = :rs_id
        """), {"rs_id": str(rs_row[0])}).fetchall()
        return [{"rule_name": r[0], "rule_definition_json": r[1], "rule_type": r[2]} for r in rows]

    rows = db.execute(text("""
        SELECT rule_name, rule_definition_json, is_active
        FROM   payroll_rule
        WHERE  workspace_id = :wid AND is_active = TRUE
        ORDER  BY rule_name
    """), {"wid": workspace_id}).mappings().all()
    return [dict(r) for r in rows]


def _load_payroll_inputs(db, employee_id, workspace_id, period_start, period_end):
    """Load inputs for this employee that would be claimed in this period.

    reference_date records when the earning/deduction occurred.  Classification:
      - reference_date IS NULL  → period-agnostic, always included
      - reference_date <= pe    → CURRENT or LATE, always included
      - reference_date > pe     → FUTURE, excluded

    Includes claimed inputs (payroll_run_id IS NOT NULL) — the simulation is
    read-only, and hiding already-claimed inputs would falsely report NOT APPLIED.
    """
    rows = db.execute(text("""
        SELECT input_code, input_category, quantity, reference_date, payroll_run_id
        FROM   payroll_input
        WHERE  employee_id  = :eid
          AND  workspace_id = :wid
          AND  (
                 reference_date IS NULL    -- period-agnostic
              OR reference_date <= :pe     -- CURRENT or LATE (never FUTURE)
               )
        ORDER  BY input_code
    """), {
        "eid": employee_id,
        "wid": workspace_id,
        "ps":  period_start,
        "pe":  period_end,
    }).fetchall()
    result: dict = {}
    for r in rows:
        code = r[0]
        if code not in result:
            result[code] = []
        result[code].append({
            "category":       r[1],
            "quantity":       float(r[2]) if r[2] is not None else None,
            "reference_date": r[3],
            "claimed":        r[4] is not None,
            "payroll_run_id": str(r[4]) if r[4] is not None else None,
        })
    return result


# ── Print sections ─────────────────────────────────────────────────────────────

def _print_title():
    console.print()
    console.rule("[bold white]PAYROLL SIMULATION ENGINE[/bold white]", style="white")
    console.print()


def _print_employee_panel(emp, ws, contract, pay_cycle, sr):
    freq      = pay_cycle.get("frequency", "—")
    run_d     = pay_cycle.get("run_day", "—")
    pay_d     = pay_cycle.get("payment_day", "—")
    proration = (pay_cycle.get("definition_json") or {}).get("proration_method", "—")
    lines = [
        f"   Employee    : {emp.get('full_name', '—')}",
        f"   Number      : {emp.get('employee_number', '—')}",
        f"   Designation : {contract.get('designation_code', '—')}",
        f"   Grade       : {contract.get('grade_code', '—')}",
        f"   Workspace   : {ws.get('name', '—')}  ({ws.get('country_code', '—')}  {ws.get('base_currency', '—')})",
        f"   Status      : {emp.get('status', '—')}",
        f"   Pay Cycle   : {freq}  (run day {run_d}, payment day {pay_d}, proration: {proration})",
        f"   Statutory   : state={sr.get('state', '—')}  v{sr.get('version', '—')}  ({sr.get('tax_method', 'CUMULATIVE')})",
    ]
    console.print(Panel(
        "\n".join(lines),
        title="[bold white]EMPLOYEE[/bold white]",
        border_style="bright_blue",
        expand=False, padding=(1, 3),
    ))
    console.print()


def _print_salary_structure(sal_def, salary_components, meta_map, currency):
    sd_code = sal_def.get("sd_code", "—")
    lines   = [
        f"   {'COMPONENT':<30} {'AMOUNT':>18}   CATEGORY",
        f"   {'─' * 62}",
    ]
    for code, amount in salary_components.items():
        mj = (meta_map.get(code) or {}).get("metadata_json") or {}
        cat = mj.get("category", "earning")
        lines.append(f"   {code:<30} {_fmt(amount, currency):>18}   {cat}")
    lines.append("")
    console.print(Panel(
        "\n".join(lines),
        title=f"[bold white]SALARY STRUCTURE  {sd_code}[/bold white]",
        border_style="green", expand=False, padding=(0, 3),
    ))
    console.print()


def _print_component_resolution(all_meta, client_overrides, salary_components, results, currency):
    console.rule("[bold blue]COMPONENT RESOLUTION[/bold blue]", style="blue")
    console.print()

    disabled_codes = {code for code, ov in client_overrides.items() if not ov.get("is_active", True)}
    running_gross  = Decimal("0")

    for i, meta in enumerate(all_meta, 1):
        code       = meta["component_code"]
        cls        = meta.get("component_class") or ""
        method     = meta.get("calculation_method") or "—"
        mj         = meta.get("metadata_json") or {}
        pri        = meta.get("execution_priority")
        suppressed = code in disabled_codes
        overridden = code in client_overrides and not suppressed

        # Source annotation
        if suppressed:
            source = "client_component_metadata  →  is_active: false"
        elif overridden:
            source = "client_component_metadata  (overrides component_metadata)"
        elif code in salary_components:
            source = "salary_definition"
        else:
            source = "component_metadata"

        fin   = mj.get("financial_role", {})
        cat   = mj.get("category") or fin.get("category") or cls or "—"
        net_e = fin.get("net_effect") or mj.get("gross_effect") or "—"
        aff_g = mj.get("gross_effect") == "increase" or fin.get("affects_gross") is True

        result_val = results.get(code) if not suppressed else None

        if suppressed:
            tag = f"[SKIP {i:>2}]"
            console.print(f"{I}[dim]{tag}  {code}[/dim]")
            console.print(f"{I}  [dim]category      : {cat}[/dim]")
            console.print(f"{I}  [red]status        : SUPPRESSED — workspace override (client_component_metadata)[/red]")
            console.print(f"{I}  [dim]source        : {source}[/dim]")

        elif pri is None:
            tag = f"[INFO {i:>2}]"
            console.print(f"{I}[dim]{tag}  {code}[/dim]")
            console.print(f"{I}  [dim]category      : {cat}[/dim]")
            console.print(f"{I}  [dim]source        : {source}[/dim]")
            console.print(f"{I}  [dim]status        : informational — no execution priority, skipped by engine[/dim]")

        else:
            tag = f"[STEP {i:>2}]"
            console.print(f"{I}[bold cyan]{tag}  {code}[/bold cyan]")
            console.print(f"{I}  category      : {cat}  [dim](source: {source})[/dim]")
            console.print(f"{I}  method        : {method}")
            console.print(f"{I}  affects_gross : {'yes' if aff_g else 'no'}")
            if net_e and net_e != "—":
                console.print(f"{I}  net_effect    : {net_e}")
            if result_val is not None:
                console.print(f"{I}  amount        : [bold]{_fmt(result_val, currency)}[/bold]")
                if cls == "earning":
                    running_gross += result_val
                    console.print(f"{I}  running gross : {_fmt(running_gross, currency)}")

        console.print()


def _print_pension_section(results, salary_components, meta_map, pension_employee_rate, pension_employer_rate, sr, currency):
    console.rule("[bold yellow]PENSION CONTRIBUTIONS[/bold yellow]", style="yellow")
    console.print()

    pensionable_base  = Decimal("0")
    pensionable_codes = []
    for code, amount in salary_components.items():
        mj = (meta_map.get(code) or {}).get("metadata_json") or {}
        if mj.get("is_pensionable"):
            pensionable_base += amount
            pensionable_codes.append(code)

    pension_emp    = results.get("PENSION_EMPLOYEE", Decimal("0"))
    pension_er     = results.get("PENSION_EMPLOYER", Decimal("0"))
    pension_cfg    = (sr.get("rules_jsonb") or {}).get("pension", {})
    tax_deductible = pension_cfg.get("tax_deductible", True)

    console.print(f"{I}Pensionable Base : {_fmt(pensionable_base, currency)}  ({' + '.join(pensionable_codes)})")
    console.print(f"{I}Rate source      : statutory_rule.pension  [FIRS v{sr.get('version', '—')}]")
    console.print(f"{I}Tax deductible   : {'yes — reduces taxable income' if tax_deductible else 'no'}")
    console.print()
    console.print(f"{I}Employee {_pct(pension_employee_rate):<10}: {_fmt(pension_emp, currency)}  [DEDUCTION — reduces net pay + tax base]")
    console.print(f"{I}Employer {_pct(pension_employer_rate):<10}: {_fmt(pension_er, currency)}  [EMPLOYER COST — not deducted from employee]")
    console.print()


def _print_payroll_rules(payroll_rules, employee_inputs, currency):
    console.rule("[bold magenta]PAYROLL RULES[/bold magenta]", style="magenta")
    console.print()

    applied = 0
    for i, rule in enumerate(payroll_rules, 1):
        name   = rule.get("rule_name", "—")
        defn   = rule.get("rule_definition_json") or {}
        method = defn.get("calculation_method", "—")
        field  = defn.get("input_field", "")
        rate   = defn.get("rate")
        amount = defn.get("amount")
        active = rule.get("is_active", True)

        input_val   = None
        claim_note  = ""
        if field and field in employee_inputs:
            events     = employee_inputs[field]  # list of event dicts
            quantities = [e.get("quantity") for e in events if e.get("quantity") is not None]
            input_val  = sum(quantities) if quantities else None
            claimed_events  = [e for e in events if e.get("claimed")]
            unclaimed_events = [e for e in events if not e.get("claimed")]
            if claimed_events and not unclaimed_events:
                claim_note = f"  [dim][{len(claimed_events)} event(s) claimed][/dim]"
            elif claimed_events:
                claim_note = (
                    f"  [dim][{len(claimed_events)} claimed, "
                    f"{len(unclaimed_events)} unclaimed — will be swept on next run][/dim]"
                )
            else:
                claim_note = f"  [dim][{len(unclaimed_events)} event(s) unclaimed — will be swept on next run][/dim]"

        if not active:
            status = "INACTIVE — rule disabled"
            impact = Decimal("0")
        elif field and input_val is None:
            status = f"NOT APPLIED — no {field!r} in employee inputs for this run"
            impact = Decimal("0")
        elif field and input_val is not None:
            impact = (Decimal(str(input_val)) * Decimal(str(rate))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if rate else Decimal(str(amount or 0))
            status = f"APPLIED — {input_val} unit(s){claim_note}"
            applied += 1
        else:
            status = "NOT APPLIED — no employee event data supplied for this run"
            impact = Decimal("0")

        console.print(f"{I}[RULE {i}]  {name}")
        console.print(f"{I}  method        : {method}")
        if field:
            console.print(f"{I}  requires      : {field}")
        if rate is not None:
            console.print(f"{I}  rate          : {_fmt(rate, currency)} / unit")
        if amount is not None:
            console.print(f"{I}  fixed amount  : {_fmt(amount, currency)}")
        console.print(f"{I}  status        : {status}")
        console.print(f"{I}  impact        : {_fmt(impact, currency)}")
        console.print()

    console.print(f"{I}{len(payroll_rules)} rules checked — {applied} applied")
    console.print()


def _print_paye_section(results, tax_bands, sr, currency):
    console.rule("[bold yellow]TAX CALCULATION (PAYE)[/bold yellow]", style="yellow")
    console.print()

    taxable_monthly = results.get("TAXABLE_INCOME", Decimal("0"))
    gross_monthly   = results.get("GROSS_PAY",      Decimal("0"))
    pension_monthly = results.get("PENSION_EMPLOYEE", Decimal("0"))
    rent_monthly    = results.get("RENT_RELIEF")
    annual_taxable  = taxable_monthly * 12
    annual_gross    = gross_monthly * 12
    annual_pension  = pension_monthly * 12
    rules_jsonb     = sr.get("rules_jsonb") or {}
    cra_enabled     = (rules_jsonb.get("reliefs") or {}).get("consolidated_relief_allowance", {}).get("enabled", False)
    tax_threshold   = rules_jsonb.get("tax_free_threshold")

    console.print(f"{I}Monthly Gross  : {_fmt(gross_monthly, currency)}")
    console.print(f"{I}Annual Gross   : {_fmt(annual_gross, currency)}  (× 12)")
    console.print(f"{I}Tax Method     : {sr.get('tax_method', 'CUMULATIVE')}  [dim](source: statutory_rule)[/dim]")
    console.print(f"{I}Statutory Rule : state={sr.get('state')}  v{sr.get('version')}")
    if tax_threshold:
        console.print(f"{I}Tax-free threshold : {_fmt(tax_threshold, currency)}  annual")
    console.print()
    console.print(f"{I}Deductible Reliefs")
    console.print(f"{I}  Annual Pension Employee : −{_fmt(annual_pension, currency)}  [dim](source: statutory_rule.pension.employee_rate)[/dim]")
    if rent_monthly is not None:
        console.print(f"{I}  Annual Rent Relief      : −{_fmt(rent_monthly * 12, currency)}  [dim](source: payroll_input.ANNUAL_RENT_PAID)[/dim]")
    else:
        console.print(f"{I}  Annual Rent Relief      : n/a  [dim](RENT_RELIEF inactive — is_active=false on component_metadata)[/dim]")
    if cra_enabled:
        console.print(f"{I}  CRA                     : see statutory_rule.reliefs.cra")
    else:
        console.print(f"{I}  CRA                     : n/a  [dim](abolished — Nigeria Tax Act 2025)[/dim]")
    console.print(f"{I}  {'─' * 52}")
    console.print(f"{I}Annual Taxable Income    : {_fmt(annual_taxable, currency)}")
    console.print()

    # Band-by-band breakdown
    hdr = f"  {'LOWER LIMIT':>16}  {'UPPER LIMIT':>16}  {'RATE':>6}  {'TAXABLE IN BAND':>18}  {'TAX IN BAND':>15}"
    sep = f"  {'─'*16}  {'─'*16}  {'─'*6}  {'─'*18}  {'─'*15}"
    console.print(f"{I}{hdr}")
    console.print(f"{I}{sep}")

    annual_paye = Decimal("0")
    for band in sorted(tax_bands, key=lambda b: b["lower_limit"]):
        lower  = Decimal(str(band["lower_limit"]))
        upper  = Decimal(str(band["upper_limit"])) if band["upper_limit"] is not None else None
        rate   = Decimal(str(band["rate"]))
        g      = Decimal(str(annual_taxable))

        if g <= lower:
            taxable_in = Decimal("0")
        elif upper is None:
            taxable_in = g - lower
        else:
            taxable_in = min(g, upper) - lower

        tax_in = (taxable_in * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        annual_paye += tax_in

        lo_s  = f"{float(lower):>16,.2f}"
        hi_s  = f"{float(upper):>16,.2f}" if upper is not None else f"{'∞':>16}"
        rt_s  = f"{float(rate)*100:>5.1f}%"
        tib_s = f"{_fmt(taxable_in):>18}" if taxable_in > 0 else f"{'—':>18}"
        txb_s = f"{_fmt(tax_in):>15}"     if taxable_in > 0 else f"{'—':>15}"
        console.print(f"{I}  {lo_s}  {hi_s}  {rt_s}  {tib_s}  {txb_s}")

    monthly_paye = (annual_paye / 12).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    console.print()
    console.print(f"{I}ANNUAL PAYE  = {_fmt(annual_paye, currency)}")
    console.print(f"{I}MONTHLY PAYE = {_fmt(monthly_paye, currency)}  (÷ 12)")
    console.print()


def _print_summary(salary_components, results, client_overrides, pension_employee_rate, pension_employer_rate, currency):
    disabled_codes = {code for code, ov in client_overrides.items() if not ov.get("is_active", True)}

    gross_pay   = results.get("GROSS_PAY",        Decimal("0"))
    pension_emp = results.get("PENSION_EMPLOYEE", Decimal("0"))
    pension_er  = results.get("PENSION_EMPLOYER", Decimal("0"))
    paye        = results.get("PAYE",             Decimal("0"))
    net_pay     = results.get("NET_PAY",          Decimal("0"))

    earn_total = sum(salary_components.values(), Decimal("0"))

    deduction_defs = [
        ("PENSION_EMPLOYEE",          f"Pension (employee {_pct(pension_employee_rate)})"),
        ("PAYE",                       "PAYE (income tax)"),
        ("NHF_CONTRIBUTION",           "NHF Contribution"),
        ("HEALTH_INSURANCE_EMPLOYEE",  "Health Insurance (employee)"),
        ("DEVELOPMENT_LEVY",           "Development Levy"),
    ]

    deduction_total = Decimal("0")
    lines = ["   EARNINGS"]
    for code, amount in salary_components.items():
        lines.append(f"     {code:<34} {_fmt(amount, currency):>18}")
    lines.append(f"   {'Total Earnings':<36} {_fmt(earn_total, currency):>18}")
    lines.append("")
    lines.append("   DEDUCTIONS")
    for code, label in deduction_defs:
        if code in disabled_codes:
            lines.append(f"     {label:<34} {'[suppressed]':>18}  [dim](client_component_metadata)[/dim]")
        else:
            val = results.get(code, Decimal("0"))
            lines.append(f"     {label:<34} {_fmt(val, currency):>18}")
            deduction_total += val
    lines.append(f"   {'Total Deductions':<36} {_fmt(deduction_total, currency):>18}")
    lines.append("")
    lines.append(f"   {'NET PAY':<36} {_fmt(net_pay, currency):>18}")
    lines.append("")

    console.rule("[bold cyan]PAYROLL SUMMARY[/bold cyan]", style="cyan")
    console.print()
    console.print(Panel("\n".join(lines), title="[bold white]PAYROLL SUMMARY[/bold white]", border_style="cyan", expand=False, padding=(0, 3)))
    console.print()

    er_lines = ["   EMPLOYER COSTS (not deducted from employee)"]
    er_lines.append(f"     {'Pension (employer ' + _pct(pension_employer_rate) + ')':<36} {_fmt(pension_er, currency):>18}")

    life_ins = results.get("LIFE_INSURANCE")
    if "LIFE_INSURANCE" in disabled_codes:
        er_lines.append(f"     {'Life Insurance':<36} {'[suppressed]':>18}  [dim](client_component_metadata)[/dim]")
    elif life_ins is not None:
        er_lines.append(f"     {'Life Insurance':<36} {_fmt(life_ins, currency):>18}")

    er_lines.append("")
    console.print(Panel("\n".join(er_lines), title="[bold white]EMPLOYER COSTS[/bold white]", border_style="dim", expand=False, padding=(0, 3)))
    console.print()
    console.rule(style="dim")
    console.print("[dim]Simulation complete — no database writes were made.[/dim]", justify="center")
    console.print()


# ── Main ───────────────────────────────────────────────────────────────────────

def simulate(employee_id=None, employee_number=None, workspace_id=None,
             period_start=None, period_end=None):
    db = SessionLocal()
    try:
        emp          = _load_employee(db, employee_id, employee_number, workspace_id)
        workspace_id = workspace_id or str(emp["workspace_id"])
        ws           = _load_workspace(db, workspace_id)
        currency     = ws.get("base_currency") or "NGN"
        country_code = ws.get("country_code") or "NG"
        contract     = _load_contract_details(db, str(emp["employee_id"]))
        pay_cycle    = _load_pay_cycle(db, workspace_id)

        sal_def, salary_components = _load_salary_components(db, str(emp["employee_id"]))

        sr, pension_employee_rate, pension_employer_rate = _load_statutory_rule(db, workspace_id)
        rules_jsonb = sr.get("rules_jsonb") or {}
        tax_bands        = _load_tax_bands(db, str(sr["statutory_rule_id"]))
        all_platform_meta = _load_component_metadata(db, country_code)
        client_overrides  = _load_client_overrides(db, workspace_id)
        payroll_rules     = _load_payroll_rules(db, workspace_id)
        # Build period context here so _load_payroll_inputs can scope by date.
        # build_period_context needs no DB connection — safe to call inside the session.
        period_ctx = build_period_context(
            period_start=period_start,
            period_end=period_end,
            period_type=pay_cycle.get("frequency"),
        )
        employee_inputs   = _load_payroll_inputs(
            db,
            str(emp["employee_id"]),
            workspace_id,
            period_ctx.period_start,
            period_ctx.period_end,
        )
        rent_relief_cfg   = rules_jsonb.get("reliefs", {}).get("rent_relief", {})
        nhf_rate                         = Decimal(str(rules_jsonb.get("nhf", {}).get("employee_rate", "0.025")))
        health_insurance_employee_amount = Decimal(str(rules_jsonb.get("health_insurance", {}).get("employee_amount", "0")))
        development_levy_amount          = Decimal(str(rules_jsonb.get("development_levy", {}).get("amount", "0")))
        life_insurance_employer_rate     = Decimal(str(rules_jsonb.get("life_insurance", {}).get("employer_rate", "0")))
    finally:
        db.close()

    # Engine receives filtered metadata (workspace suppressions applied)
    disabled_codes  = {code for code, ov in client_overrides.items() if not ov.get("is_active", True)}
    engine_metadata = [m for m in all_platform_meta if m["component_code"] not in disabled_codes]
    meta_map        = {m["component_code"]: m for m in all_platform_meta}

    # Apply flat-amount client_component_metadata overrides (mirrors production payroll.py)
    if "DEVELOPMENT_LEVY" in client_overrides and "monthly_amount" in client_overrides["DEVELOPMENT_LEVY"]:
        development_levy_amount = Decimal(str(client_overrides["DEVELOPMENT_LEVY"]["monthly_amount"]))
    if "HEALTH_INSURANCE_EMPLOYEE" in client_overrides and "employee_monthly_amount" in client_overrides["HEALTH_INSURANCE_EMPLOYEE"]:
        health_insurance_employee_amount = Decimal(str(client_overrides["HEALTH_INSURANCE_EMPLOYEE"]["employee_monthly_amount"]))

    # Build client_meta: global component_metadata.metadata_json as base layer,
    # workspace overrides on top — mirrors the production /payroll/run route.
    client_meta = {m["component_code"]: dict(m.get("metadata_json") or {}) for m in engine_metadata}
    for code, ws_override in client_overrides.items():
        if code not in client_meta:
            client_meta[code] = {}
        for key, val in ws_override.items():
            if (
                key in client_meta[code]
                and isinstance(client_meta[code][key], dict)
                and isinstance(val, dict)
            ):
                client_meta[code][key] = {**client_meta[code][key], **val}
            else:
                client_meta[code][key] = val

    # Apply workspace payroll rules to salary_components before the engine.
    # employee_inputs is {code: [events]} — each event carries its own reference_date.
    # (mirrors the production _run_sequential path in executor.py)
    if payroll_rules:
        salary_components, _rule_trace = apply_payroll_rules(
            salary_components=salary_components,
            payroll_rules=payroll_rules,
            employee_inputs=employee_inputs,
            client_meta=client_meta,
            working_days=period_ctx.working_days,
            calendar_days=period_ctx.calendar_days,
        )

    context = {
        "tax_bands":                        tax_bands,
        "pension_employee_rate":            pension_employee_rate,
        "pension_employer_rate":            pension_employer_rate,
        "rent_relief_cfg":                  rent_relief_cfg,
        "nhf_rate":                         nhf_rate,
        "health_insurance_employee_amount": health_insurance_employee_amount,
        "development_levy_amount":          development_levy_amount,
        "life_insurance_employer_rate":     life_insurance_employer_rate,
        "employee_inputs":                  employee_inputs,
        "client_meta":                      client_meta,
        "period":                           period_ctx,
        "payroll_rules":                    payroll_rules,
        # Simulation has no cross-period inputs; stubs match production context shape.
        "historical_rule_sets":            [],
        "historical_period_contexts":      {},
        "current_rule_set_id":             None,
        "current_rule_set_effective_from": None,
    }

    engine_metadata = build_runtime_component_registry(
        platform_metadata=engine_metadata,
        payroll_rules=payroll_rules,
        employee_inputs=employee_inputs,
    )
    output  = run_sequential_payroll(salary_components, engine_metadata, context)
    results = output["results"]

    # ── Output ────────────────────────────────────────────────────────────────
    _print_title()
    _print_employee_panel(emp, ws, contract, pay_cycle, sr)
    _print_salary_structure(sal_def, salary_components, meta_map, currency)
    _print_component_resolution(all_platform_meta, client_overrides, salary_components, results, currency)
    _print_pension_section(results, salary_components, meta_map, pension_employee_rate, pension_employer_rate, sr, currency)
    _print_payroll_rules(payroll_rules, employee_inputs, currency)
    _print_paye_section(results, tax_bands, sr, currency)
    _print_summary(salary_components, results, client_overrides, pension_employee_rate, pension_employer_rate, currency)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Simulate the sequential payroll engine for one employee (read-only).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backend/scripts/simulate_payroll.py
  python backend/scripts/simulate_payroll.py --employee-number EMP001
  python backend/scripts/simulate_payroll.py --workspace-id <uuid> --employee-number EMP001
        """,
    )
    parser.add_argument("employee_id",       nargs="?", default=None, metavar="EMPLOYEE_ID")
    parser.add_argument("--employee-id",     dest="employee_id_flag", metavar="UUID")
    parser.add_argument("--employee-number", metavar="CODE")
    parser.add_argument("--workspace-id",    metavar="UUID")
    parser.add_argument("--period-start",    metavar="YYYY-MM-DD", help="Period start date (default: first of current month)")
    parser.add_argument("--period-end",      metavar="YYYY-MM-DD", help="Period end date (default: last of period_start month)")
    args = parser.parse_args()

    eid = args.employee_id_flag or args.employee_id
    simulate(
        employee_id=eid,
        employee_number=args.employee_number,
        workspace_id=args.workspace_id,
        period_start=args.period_start,
        period_end=args.period_end,
    )


if __name__ == "__main__":
    main()
