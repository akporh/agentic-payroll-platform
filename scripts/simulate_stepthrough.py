#!/usr/bin/env python3
"""
Step-through simulation — drives the REAL run_sequential_payroll() engine.

Phase 1   : DB loading       — each SQL query shown as a numbered step,
                               including client_component_metadata + payroll_rule.
Phase 2   : Input assembly   — salary_components / component_metadata / context.
Phase 2.5 : Payroll rules    — apply_payroll_rules() evaluated before the executor.
Phase 3   : Engine replay    — walks the engine's own execution trace entry-by-entry,
                               printing the exact code block from sequential_executor.py.
"""
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv; load_dotenv()  # noqa: E402

from sqlalchemy import text
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.table import Table

from backend.infra.db.session import SessionLocal
from backend.domain.payroll.sequential_executor import run_sequential_payroll
from backend.domain.payroll.rule_evaluator import apply_payroll_rules

console = Console(highlight=False)

# ── Code snippets from sequential_executor.py shown during the trace replay ──
ENGINE_CODE = {
    "salary_component": (
        "# execution_priority: 10–40  (each earning in salary_def)\n"
        "results[code] = Decimal(str(salary_components.get(code, '0')))"
    ),
    "sum_earnings": (
        "# GROSS_PAY  (execution_priority: 100)\n"
        "results[code] = sum(\n"
        "    v for k, v in results.items()\n"
        "    if component_map[k]['component_class'] == 'earning'\n"
        ")"
    ),
    "pension_rule": (
        "# PENSION_EMPLOYEE / PENSION_EMPLOYER  (execution_priority: 200)\n"
        "# pensionable_codes driven by client_meta.legal_role.is_pensionable\n"
        "pensionable_codes = {\n"
        "    code for code, meta in client_meta.items()\n"
        "    if meta['legal_role']['is_pensionable']\n"
        "}\n"
        "pensionable_base = sum(results[c] for c in pensionable_codes if c in results)\n"
        "pension_employee, pension_employer = calculate_pension(\n"
        "    pensionable_base, pension_employee_rate, pension_employer_rate\n"
        ")\n"
        "results['PENSION_EMPLOYEE'] = pension_employee\n"
        "results['PENSION_EMPLOYER'] = pension_employer"
    ),
    "rent_relief": (
        "# RENT_RELIEF  (execution_priority: 250)\n"
        "# Skipped if ANNUAL_RENT_PAID is absent or zero (on_ineligible='skip')\n"
        "resolved         = _resolve_inputs(meta_json['input_requirements'], employee_inputs)\n"
        "annual_rent_paid = resolved.get('ANNUAL_RENT_PAID', Decimal('0'))\n"
        "rate = Decimal(str(rent_relief_cfg.get('rate', '0')))\n"
        "cap  = Decimal(str(rent_relief_cfg.get('cap',  '0')))\n"
        "results[code] = calculate_rent_relief(annual_rent_paid, rate, cap)"
    ),
    "taxable_income": (
        "# TAXABLE_INCOME  (execution_priority: 300)\n"
        "results[code] = (\n"
        "    results['GROSS_PAY']\n"
        "    - results.get('PENSION_EMPLOYEE', Decimal('0'))\n"
        "    - results.get('RENT_RELIEF',      Decimal('0'))  # 0 if skipped\n"
        ").quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)"
    ),
    "paye_rule": (
        "# PAYE  (execution_priority: 400)\n"
        "# TAXABLE_INCOME already has pension + rent relief subtracted\n"
        "results[code] = calculate_monthly_paye(\n"
        "    results.get('TAXABLE_INCOME', Decimal('0')), tax_bands\n"
        ")"
    ),
    "net_formula": (
        "# NET_PAY  (execution_priority: 500)\n"
        "# Sums all components with component_class == 'statutory_deduction'\n"
        "total_deductions = sum(\n"
        "    v for k, v in results.items()\n"
        "    if component_map.get(k, {}).get('component_class') == 'statutory_deduction'\n"
        ")\n"
        "results[code] = (\n"
        "    results['GROSS_PAY'] - total_deductions\n"
        ").quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)"
    ),
    "pension_employer": (
        "# PENSION_EMPLOYER  (execution_priority: 210)\n"
        "# Already set by pension_rule — this step surfaces it in the trace\n"
        "results[code] = results.get('PENSION_EMPLOYER', Decimal('0'))"
    ),
}

STEP_N = 0


def step(header: str, code: str, result_label: str = "", result_value=None):
    global STEP_N
    STEP_N += 1
    console.print()
    console.rule(f"[bold yellow]STEP {STEP_N}  —  {header}[/bold yellow]", style="dim yellow")
    console.print(Syntax(code, "python", theme="monokai", word_wrap=True))
    if result_label:
        tag = f"[bold cyan]  ⟶  {result_label}[/bold cyan]"
        if result_value is not None:
            console.print(tag + f"  =  [bold white]{result_value}[/bold white]")
        else:
            console.print(tag)


def _fmt(amount, currency="NGN"):
    if amount is None or str(amount) == "None":
        return "—"
    return f"{currency} {Decimal(str(amount)):,.2f}"


# ─────────────────────────────────────────────────────────────────────────────
def run(employee_id: str):
    session = SessionLocal()
    console.print()
    console.rule("[bold cyan]STEP-THROUGH  ·  run_sequential_payroll()[/bold cyan]", style="cyan")
    console.print(f"[dim]  sequential_executor.py  ·  employee {employee_id}[/dim]")

    # ── PHASE 1 : DB LOADING ─────────────────────────────────────────────────
    console.print()
    console.rule("[bold magenta]PHASE 1 — DB LOADING[/bold magenta]", style="magenta")

    # 1. Employee
    step(
        "employee",
        f"emp_row = session.execute(\n"
        f"    text('SELECT * FROM employee WHERE employee_id = :eid'),\n"
        f"    {{'eid': '{employee_id}'}}\n"
        f").mappings().first()",
    )
    emp_row = session.execute(
        text("SELECT * FROM employee WHERE employee_id = :eid"), {"eid": employee_id}
    ).mappings().first()
    emp = dict(emp_row)
    console.print(f"  [dim]full_name={emp['full_name']}  "
                  f"employee_number={emp['employee_number']}  "
                  f"status={emp['status']}[/dim]")

    workspace_id = str(emp["workspace_id"])

    # 2. Workspace
    step(
        "workspace",
        f"ws = session.execute(\n"
        f"    text('SELECT * FROM workspace WHERE workspace_id = :wid'),\n"
        f"    {{'wid': '{workspace_id}'}}\n"
        f").mappings().first()",
    )
    ws_row = session.execute(
        text("SELECT * FROM workspace WHERE workspace_id = :wid"), {"wid": workspace_id}
    ).mappings().first()
    ws = dict(ws_row)
    console.print(f"  [dim]name={ws['name']}  country={ws['country_code']}  "
                  f"currency={ws['base_currency']}[/dim]")

    currency = ws["base_currency"] or "NGN"
    country  = ws["country_code"]  or "NG"

    # 3. Active contract
    step(
        "employee_contract",
        "contract = session.execute(text(\"\"\"\n"
        "    SELECT ec.*, d.designation_code, g.grade_code\n"
        "    FROM employee_contract ec\n"
        "    LEFT JOIN designation d ON d.designation_id = ec.designation_id\n"
        "    LEFT JOIN grade g ON g.grade_id = ec.grade_id\n"
        "    WHERE ec.employee_id = :eid\n"
        "      AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)\n"
        "    ORDER BY ec.start_date DESC LIMIT 1\n"
        "\"\"\"), {'eid': ...}).mappings().first()",
    )
    contract_row = session.execute(
        text("""
            SELECT ec.*, d.designation_code, g.grade_code
            FROM employee_contract ec
            LEFT JOIN designation d ON d.designation_id = ec.designation_id
            LEFT JOIN grade g ON g.grade_id = ec.grade_id
            WHERE ec.employee_id = :eid
              AND (ec.end_date IS NULL OR ec.end_date >= CURRENT_DATE)
            ORDER BY ec.start_date DESC LIMIT 1
        """),
        {"eid": str(emp["employee_id"])},
    ).mappings().first()
    contract = dict(contract_row) if contract_row else {}
    console.print(f"  [dim]designation={contract.get('designation_code')}  "
                  f"grade={contract.get('grade_code')}  "
                  f"salary_definition_id={contract.get('salary_definition_id')}[/dim]")

    # 4. Salary definition → salary_components dict
    step(
        "salary_definition  →  salary_components",
        "sd = session.execute(\n"
        "    text('SELECT * FROM salary_definition WHERE salary_definition_id = :sid'),\n"
        "    {'sid': contract['salary_definition_id']}\n"
        ").mappings().first()\n"
        "\n"
        "# Build salary_components: the dict run_sequential_payroll() expects\n"
        "salary_components = {\n"
        "    code: Decimal(str(amount))\n"
        "    for code, amount in sd['components_jsonb'].items()\n"
        "}",
    )
    sd_row = session.execute(
        text("SELECT * FROM salary_definition WHERE salary_definition_id = :sid"),
        {"sid": str(contract["salary_definition_id"])},
    ).mappings().first()
    sd = dict(sd_row)
    salary_components = {k: Decimal(str(v)) for k, v in sd["components_jsonb"].items()}
    for code, amount in salary_components.items():
        console.print(f"  [dim]salary_components['{code}'] = {_fmt(amount, currency)}[/dim]")

    # 5. Statutory rule + pension config
    step(
        "statutory_rule  →  pension rates",
        "sr = session.execute(\n"
        "    text(\"\"\"\n"
        "        SELECT * FROM statutory_rule\n"
        "        WHERE country_code = :cc\n"
        "        ORDER BY version DESC LIMIT 1\n"
        "    \"\"\"),\n"
        "    {'cc': country}\n"
        ").mappings().first()\n"
        "\n"
        "pension_cfg            = sr['rules_jsonb']['pension']\n"
        "pension_employee_rate  = Decimal(str(pension_cfg['employee_rate']))\n"
        "pension_employer_rate  = Decimal(str(pension_cfg['employer_rate']))\n"
        "rent_relief_cfg        = sr['rules_jsonb']['reliefs']['rent_relief']",
    )
    sr_row = session.execute(
        text("""
            SELECT * FROM statutory_rule
            WHERE country_code = :cc
            ORDER BY version DESC LIMIT 1
        """),
        {"cc": country},
    ).mappings().first()
    sr = dict(sr_row)
    rules_jsonb           = sr.get("rules_jsonb") or {}
    pension_cfg           = rules_jsonb.get("pension", {})
    pension_employee_rate = Decimal(str(pension_cfg.get("employee_rate", "0.09")))
    pension_employer_rate = Decimal(str(pension_cfg.get("employer_rate", "0.10")))
    rent_relief_cfg       = rules_jsonb.get("reliefs", {}).get("rent_relief", {})
    console.print(f"  [dim]state={sr['state']}  version={sr['version']}  "
                  f"tax_method={sr['tax_method']}[/dim]")
    console.print(f"  [dim]pension_employee_rate={pension_employee_rate}  "
                  f"pension_employer_rate={pension_employer_rate}[/dim]")
    console.print(f"  [dim]rent_relief_cfg={rent_relief_cfg}[/dim]")

    # 6. Tax bands
    step(
        "tax_band",
        "bands = session.execute(\n"
        "    text('SELECT * FROM tax_band WHERE statutory_rule_id = :sid ORDER BY lower_limit'),\n"
        "    {'sid': sr['statutory_rule_id']}\n"
        ").mappings().all()\n"
        "\n"
        "tax_bands = [\n"
        "    {'lower_limit': float(b['lower_limit']),\n"
        "     'upper_limit': float(b['upper_limit']) if b['upper_limit'] else None,\n"
        "     'rate':        float(b['rate'])}\n"
        "    for b in bands\n"
        "]",
    )
    band_rows = session.execute(
        text("SELECT * FROM tax_band WHERE statutory_rule_id = :sid ORDER BY lower_limit"),
        {"sid": str(sr_row["statutory_rule_id"])},
    ).mappings().all()
    tax_bands = [
        {
            "lower_limit": float(b["lower_limit"]),
            "upper_limit": float(b["upper_limit"]) if b.get("upper_limit") is not None else None,
            "rate":        float(b["rate"]),
        }
        for b in band_rows
    ]
    for b in tax_bands:
        upper = f"{b['upper_limit']:,.0f}" if b["upper_limit"] else "∞"
        console.print(f"  [dim]  {b['lower_limit']:>14,.0f} – {upper:<14}  "
                      f"@ {b['rate']*100:.1f}%[/dim]")

    # 7. Component metadata
    step(
        "component_metadata  (platform, country=" + country + ")",
        "meta_rows = session.execute(\n"
        "    text(\"\"\"\n"
        "        SELECT component_code, component_class, calculation_method,\n"
        "               execution_priority, is_active, metadata_json\n"
        "        FROM component_metadata\n"
        "        WHERE country_code = :cc AND is_active = true\n"
        "        ORDER BY execution_priority NULLS LAST\n"
        "    \"\"\"),\n"
        "    {'cc': country_code}\n"
        ").mappings().all()\n"
        "\n"
        "component_metadata = [dict(r) for r in meta_rows]",
    )
    meta_rows = session.execute(
        text("""
            SELECT component_code, component_class, calculation_method,
                   execution_priority, is_active, metadata_json
            FROM component_metadata
            WHERE country_code = :cc AND is_active = true
            ORDER BY execution_priority NULLS LAST
        """),
        {"cc": country},
    ).mappings().all()
    component_metadata = [dict(r) for r in meta_rows]
    for m in component_metadata:
        pri = str(m["execution_priority"]) if m["execution_priority"] is not None else "—"
        console.print(f"  [dim]  [{pri:>4}]  {m['component_code']:<28} "
                      f"method={m['calculation_method'] or '—'}[/dim]")

    # 8. client_component_metadata → client_meta dict
    step(
        "client_component_metadata  (workspace-level flags)",
        "ccm_rows = session.execute(\n"
        "    text(\"\"\"\n"
        "        SELECT component_code, overrides_json\n"
        "        FROM client_component_metadata\n"
        "        WHERE workspace_id = :wid\n"
        "    \"\"\"),\n"
        "    {'wid': workspace_id}\n"
        ").mappings().all()\n"
        "\n"
        "# Build client_meta: {component_code: overrides_json}\n"
        "# Keys used by engine: legal_role.is_pensionable, legal_role.is_taxable,\n"
        "#                      calculations_behaviour.proration_strategy\n"
        "client_meta = {r['component_code']: r['overrides_json'] for r in ccm_rows}",
    )
    ccm_rows = session.execute(
        text("""
            SELECT component_code, overrides_json
            FROM client_component_metadata
            WHERE workspace_id = :wid
        """),
        {"wid": workspace_id},
    ).mappings().all()
    client_meta = {r["component_code"]: r["overrides_json"] for r in ccm_rows}
    for code, meta in client_meta.items():
        lr = meta.get("legal_role", {})
        cb = meta.get("calculations_behaviour", {})
        console.print(
            f"  [dim]  {code:<28} "
            f"is_pensionable={lr.get('is_pensionable')}  "
            f"is_taxable={lr.get('is_taxable')}  "
            f"is_active={meta.get('is_active', True)}  "
            f"proration={cb.get('proration_strategy')}[/dim]"
        )

    # Suppress disabled components (mirrors production payroll.py behaviour)
    disabled_codes = {
        code for code, ov in client_meta.items()
        if not ov.get("is_active", True)
    }
    if disabled_codes:
        component_metadata = [
            m for m in component_metadata
            if m["component_code"] not in disabled_codes
        ]
        console.print(f"  [dim]  suppressed {len(disabled_codes)} disabled component(s): {disabled_codes}[/dim]")

    # 9. payroll_rule → payroll_rules list
    step(
        "payroll_rule  (workspace rules)",
        "pr_rows = session.execute(\n"
        "    text(\"\"\"\n"
        "        SELECT rule_name, rule_type, rule_definition_json, is_active\n"
        "        FROM payroll_rule\n"
        "        WHERE workspace_id = :wid AND is_active = true\n"
        "    \"\"\"),\n"
        "    {'wid': workspace_id}\n"
        ").mappings().all()\n"
        "\n"
        "payroll_rules = [dict(r) for r in pr_rows]",
    )
    pr_rows = session.execute(
        text("""
            SELECT rule_name, rule_type, rule_definition_json, is_active
            FROM payroll_rule
            WHERE workspace_id = :wid AND is_active = true
        """),
        {"wid": workspace_id},
    ).mappings().all()
    payroll_rules = [dict(r) for r in pr_rows]
    for r in payroll_rules:
        defn = r.get("rule_definition_json") or {}
        console.print(
            f"  [dim]  {r['rule_name']:<28} "
            f"method={defn.get('calculation_method')}  "
            f"input={defn.get('input_field', '—')}[/dim]"
        )

    # 10. payroll_input → employee_inputs dict
    step(
        "payroll_input  (unclaimed inputs for this employee)",
        "input_rows = session.execute(\n"
        "    text(\"\"\"\n"
        "        SELECT input_code, input_category, quantity, rate, amount\n"
        "        FROM payroll_input\n"
        "        WHERE employee_id = :eid AND payroll_run_id IS NULL\n"
        "    \"\"\"),\n"
        "    {'eid': employee_id}\n"
        ").fetchall()\n"
        "\n"
        "employee_inputs = {\n"
        "    r[0]: {'category': r[1], 'quantity': r[2], 'rate': r[3], 'amount': r[4]}\n"
        "    for r in input_rows\n"
        "}",
    )
    input_rows = session.execute(
        text("""
            SELECT input_code, input_category, quantity, rate, amount
            FROM payroll_input
            WHERE employee_id = :eid AND payroll_run_id IS NULL
        """),
        {"eid": str(emp["employee_id"])},
    ).fetchall()
    employee_inputs = {
        r[0]: {"category": r[1], "quantity": r[2], "rate": r[3], "amount": r[4]}
        for r in input_rows
    }
    if employee_inputs:
        for code, inp in employee_inputs.items():
            console.print(f"  [dim]  {code:<28} amount={inp['amount']}  category={inp['category']}[/dim]")
    else:
        console.print("  [dim]  (no unclaimed payroll inputs for this employee)[/dim]")

    session.close()

    # ── PHASE 2 : ASSEMBLE INPUTS ────────────────────────────────────────────
    console.print()
    console.rule("[bold magenta]PHASE 2 — ASSEMBLE INPUTS[/bold magenta]", style="magenta")

    step(
        "context dict",
        "context = {\n"
        "    'tax_bands':             tax_bands,\n"
        "    'pension_employee_rate': pension_employee_rate,\n"
        "    'pension_employer_rate': pension_employer_rate,\n"
        "    'rent_relief_cfg':       rent_relief_cfg,\n"
        "    'employee_inputs':       employee_inputs,\n"
        "    'client_meta':           client_meta,\n"
        "}",
    )
    context = {
        "tax_bands":             tax_bands,
        "pension_employee_rate": pension_employee_rate,
        "pension_employer_rate": pension_employer_rate,
        "rent_relief_cfg":       rent_relief_cfg,
        "employee_inputs":       employee_inputs,
        "client_meta":           client_meta,
    }
    console.print(f"  [dim]pension_employee_rate = {context['pension_employee_rate']}[/dim]")
    console.print(f"  [dim]pension_employer_rate = {context['pension_employer_rate']}[/dim]")
    console.print(f"  [dim]rent_relief_cfg        = {rent_relief_cfg}[/dim]")
    console.print(f"  [dim]employee_inputs        = {len(employee_inputs)} input(s)[/dim]")
    console.print(f"  [dim]client_meta            = {len(client_meta)} component(s)[/dim]")
    console.print(f"  [dim]tax_bands              = {len(tax_bands)} band(s)[/dim]")

    # ── PHASE 2.5 : PAYROLL RULES ─────────────────────────────────────────────
    console.print()
    console.rule("[bold magenta]PHASE 2.5 — PAYROLL RULES (apply_payroll_rules())[/bold magenta]", style="magenta")

    step(
        "apply_payroll_rules()",
        "from backend.domain.payroll.rule_evaluator import apply_payroll_rules\n"
        "\n"
        "# employee_inputs would contain event data for this pay period:\n"
        "#   {'regular_overtime_days': 2, 'shift_days': 5, ...}\n"
        "# No event data supplied in this simulation run.\n"
        "employee_inputs = {}\n"
        "\n"
        "salary_components, rule_trace = apply_payroll_rules(\n"
        "    salary_components = salary_components,\n"
        "    payroll_rules     = payroll_rules,\n"
        "    employee_inputs   = employee_inputs,\n"
        "    client_meta       = client_meta,\n"
        ")",
    )
    employee_inputs = {}
    salary_components, rule_trace = apply_payroll_rules(
        salary_components=salary_components,
        payroll_rules=payroll_rules,
        employee_inputs=employee_inputs,
        client_meta=client_meta,
    )

    for entry in rule_trace:
        status_colour = "green" if entry["status"] == "applied" else "dim"
        console.print(
            f"  [{status_colour}]  {entry['rule']:<28} "
            f"status={entry['status']:<12} "
            f"amount={entry['amount']:<12} "
            f"note={entry['note']}[/{status_colour}]"
        )

    step(
        "call run_sequential_payroll()",
        "from backend.domain.payroll.sequential_executor import run_sequential_payroll\n"
        "\n"
        "output = run_sequential_payroll(\n"
        "    salary_components  = salary_components,\n"
        "    component_metadata = component_metadata,\n"
        "    context            = context,\n"
        ")",
    )
    output = run_sequential_payroll(salary_components, component_metadata, context)

    results = output["results"]
    trace   = output["trace"]

    console.print(f"  [bold green]✓ engine returned {len(trace)} trace entries + results dict[/bold green]")

    # ── PHASE 3 : ENGINE TRACE REPLAY ───────────────────────────────────────
    console.print()
    console.rule("[bold magenta]PHASE 3 — ENGINE EXECUTION TRACE[/bold magenta]", style="magenta")
    console.print("[dim]  Replaying output['trace'] — one entry per component executed[/dim]")

    for entry in trace:
        component = entry["component"]
        method    = entry["method"]
        result    = entry["result"]

        code_snippet = ENGINE_CODE.get(method, f"# method: {method}\nresults['{component}'] = ...")

        step(
            f"{component}  ({method})",
            code_snippet,
            result_label=f"results['{component}']",
            result_value=_fmt(result, currency),
        )

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    console.print()
    console.rule("[bold cyan]FINAL RESULT  —  results dict[/bold cyan]", style="cyan")

    t = Table(show_header=True, header_style="bold white", box=None, padding=(0, 2))
    t.add_column("Component",  style="cyan")
    t.add_column("Amount",     justify="right", style="bold white")
    t.add_column("Role",       style="dim")

    CLASS_ROLE = {
        "earning":             "earning",
        "aggregate":           "aggregate",
        "statutory_deduction": "deduction",
        "statutory_relief":    "relief",
        "final":               "final",
    }
    class_map = {m["component_code"]: m.get("component_class") for m in component_metadata}

    for code, value in results.items():
        cls  = class_map.get(code, "")
        role = CLASS_ROLE.get(cls, cls or "—")
        t.add_row(code, _fmt(value, currency), role)

    console.print(t)

    gross       = results.get("GROSS_PAY",        Decimal("0"))
    pension     = results.get("PENSION_EMPLOYEE", Decimal("0"))
    rent_relief = results.get("RENT_RELIEF")
    paye        = results.get("PAYE",             Decimal("0"))
    net         = results.get("NET_PAY",          Decimal("0"))

    console.print()
    console.print(f"  [bold green]Gross Pay           [/bold green] : {_fmt(gross, currency)}")
    console.print(f"  [bold red]  − Pension          [/bold red] : {_fmt(pension, currency)}")
    if rent_relief is not None:
        console.print(f"  [bold bright_magenta]  − Rent Relief (↓ tax)[/bold bright_magenta] : {_fmt(rent_relief, currency)}")
    console.print(f"  [bold red]  − PAYE             [/bold red] : {_fmt(paye, currency)}")
    console.print(f"  [bold cyan]= Net Pay           [/bold cyan] : [bold]{_fmt(net, currency)}[/bold]")
    console.print()
    console.rule(style="dim")
    console.print(f"[dim]  {STEP_N} steps shown  ·  {len(trace)} engine trace entries  ·  no DB writes[/dim]")
    console.print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Step-through payroll simulation using run_sequential_payroll()")
    parser.add_argument("--employee-id", default="07bef751-2309-4bbc-ad8c-bafaf30d4a21",
                        help="Employee UUID (default: John Doe / EMP001)")
    args = parser.parse_args()
    run(args.employee_id)
