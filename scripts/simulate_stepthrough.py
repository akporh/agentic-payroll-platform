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
from backend.domain.payroll.period_context import build_period_context

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
def run(employee_id: str, workspace_id: str | None = None,
        period_start: str | None = None, period_end: str | None = None):
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

    workspace_id = workspace_id or str(emp["workspace_id"])

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
    rules_jsonb = sr.get("rules_jsonb") or {}
    pension_cfg = rules_jsonb.get("pension")
    if not pension_cfg or "employee_rate" not in pension_cfg or "employer_rate" not in pension_cfg:
        console.print("[bold red]Statutory rule is missing pension rates. Run the pension rates migration.[/bold red]")
        raise SystemExit(1)
    pension_employee_rate = Decimal(str(pension_cfg["employee_rate"]))
    pension_employer_rate = Decimal(str(pension_cfg["employer_rate"]))
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
    client_overrides = {r["component_code"]: r["overrides_json"] for r in ccm_rows}

    # Build client_meta: global component_metadata.metadata_json as base,
    # workspace overrides on top — mirrors the production /payroll/run route.
    client_meta = {m["component_code"]: dict(m.get("metadata_json") or {}) for m in component_metadata}
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

    for code, meta in client_meta.items():
        lr = meta.get("legal_role", {})
        cb = meta.get("calculations_behaviour", {})
        is_ws_override = code in client_overrides
        console.print(
            f"  [dim]  {code:<28} "
            f"is_pensionable={lr.get('is_pensionable')}  "
            f"is_taxable={lr.get('is_taxable')}  "
            f"is_active={meta.get('is_active', True)}  "
            f"proration={cb.get('proration_strategy')}"
            f"{'  [ws override]' if is_ws_override else '  [global default]'}[/dim]"
        )

    # Suppress disabled components (mirrors production payroll.py behaviour)
    disabled_codes = {
        code for code, ov in client_overrides.items()
        if not ov.get("is_active", True)
    }
    if disabled_codes:
        component_metadata = [
            m for m in component_metadata
            if m["component_code"] not in disabled_codes
        ]
        console.print(f"  [dim]  suppressed {len(disabled_codes)} disabled component(s): {disabled_codes}[/dim]")

    # 9. rules — try rule_set (temporal) first, fall back to legacy payroll_rule
    from datetime import date as _date
    today_str = str(_date.today())
    step(
        "rule_set / payroll_rule  (workspace rules)",
        "# Try temporal rule_set first; fall back to legacy payroll_rule table.\n"
        "rs_row = session.execute(text(\"\"\"\n"
        "    SELECT rule_set_id FROM rule_set\n"
        "    WHERE workspace_id = :wid AND effective_from <= :today\n"
        "    ORDER BY effective_from DESC, created_at DESC LIMIT 1\n"
        "\"\"\"), {'wid': workspace_id, 'today': today}).fetchone()\n"
        "\n"
        "if rs_row:\n"
        "    payroll_rules = [dict from rule_set_item where rule_set_id = rs_row[0]]\n"
        "else:\n"
        "    payroll_rules = [dict from payroll_rule where workspace_id = :wid and is_active = true]",
    )
    rs_row = session.execute(
        text("""
            SELECT rule_set_id FROM rule_set
            WHERE workspace_id  = :wid
              AND effective_from <= :today
            ORDER BY effective_from DESC, created_at DESC
            LIMIT 1
        """),
        {"wid": workspace_id, "today": today_str},
    ).fetchone()

    current_rule_set_id = None
    if rs_row:
        current_rule_set_id = str(rs_row[0])
        item_rows = session.execute(
            text("""
                SELECT rule_name, rule_definition_json, rule_type
                FROM rule_set_item
                WHERE rule_set_id = :rs_id
            """),
            {"rs_id": current_rule_set_id},
        ).fetchall()
        payroll_rules = [
            {"rule_name": r[0], "rule_definition_json": r[1], "rule_type": r[2]}
            for r in item_rows
        ]
        console.print(f"  [dim]  rule_set {current_rule_set_id}  ({len(payroll_rules)} items)[/dim]")
    else:
        pr_rows = session.execute(
            text("""
                SELECT rule_name, rule_type, rule_definition_json, is_active
                FROM payroll_rule
                WHERE workspace_id = :wid AND is_active = true
            """),
            {"wid": workspace_id},
        ).mappings().all()
        payroll_rules = [dict(r) for r in pr_rows]
        console.print(f"  [dim]  (legacy payroll_rule table — {len(payroll_rules)} rules)[/dim]")

    for r in payroll_rules:
        defn = r.get("rule_definition_json") or {}
        console.print(
            f"  [dim]  {r['rule_name']:<28} "
            f"method={defn.get('calculation_method')}  "
            f"input={defn.get('input_field', '—')}[/dim]"
        )

    # 10b. Pay cycle — fetched first so period_ctx can be built before the payroll_input query
    pay_cycle_row = session.execute(
        text("SELECT frequency FROM pay_cycle WHERE workspace_id = :wid AND is_active = TRUE LIMIT 1"),
        {"wid": workspace_id},
    ).mappings().first()
    pay_cycle_frequency = pay_cycle_row["frequency"] if pay_cycle_row else None

    period_ctx = build_period_context(
        period_start=period_start,
        period_end=period_end,
        period_type=pay_cycle_frequency,
    )

    # 10. payroll_input → employee_inputs dict
    step(
        "payroll_input  (unclaimed inputs for this employee + period)",
        "input_rows = session.execute(\n"
        "    text(\"\"\"\n"
        "        SELECT input_code, input_category, quantity, reference_date, payroll_run_id\n"
        "        FROM payroll_input\n"
        "        WHERE employee_id  = :eid\n"
        "          AND workspace_id = :wid\n"
        "          AND (\n"
        "                reference_date IS NULL    -- period-agnostic\n"
        "             OR reference_date <= :pe     -- CURRENT or LATE (never FUTURE)\n"
        "              )\n"
        "        ORDER BY input_code\n"
        "    \"\"\"),\n"
        "    {'eid': employee_id, 'wid': workspace_id, 'pe': period_end}\n"
        ").fetchall()\n"
        "\n"
        "employee_inputs = {}\n"
        "for r in input_rows:\n"
        "    code = r[0]\n"
        "    if code not in employee_inputs:\n"
        "        employee_inputs[code] = []\n"
        "    employee_inputs[code].append({\n"
        "        'category': r[1], 'quantity': r[2], 'reference_date': r[3], 'claimed': r[4] is not None\n"
        "    })",
    )
    input_rows = session.execute(
        text("""
            SELECT input_code, input_category, quantity, reference_date, payroll_run_id
            FROM payroll_input
            WHERE employee_id  = :eid
              AND workspace_id = :wid
              AND (
                    reference_date IS NULL    -- period-agnostic
                 OR reference_date <= :pe     -- CURRENT or LATE (never FUTURE)
              )
            ORDER BY input_code
        """),
        {
            "eid": str(emp["employee_id"]),
            "wid": workspace_id,
            "pe":  period_ctx.period_end,
        },
    ).fetchall()
    employee_inputs: dict = {}
    for r in input_rows:
        code = r[0]
        if code not in employee_inputs:
            employee_inputs[code] = []
        employee_inputs[code].append({
            "category":       r[1],
            "quantity":       float(r[2]) if r[2] is not None else None,
            "reference_date": r[3],
            "claimed":        r[4] is not None,
        })
    if employee_inputs:
        for code, events in employee_inputs.items():
            for ev in events:
                claimed_note = " [claimed]" if ev["claimed"] else " [unclaimed]"
                console.print(
                    f"  [dim]  {code:<28} qty={ev['quantity']}  "
                    f"ref={ev['reference_date']}  category={ev['category']}{claimed_note}[/dim]"
                )
    else:
        console.print("  [dim]  (no payroll inputs for this employee in this period)[/dim]")

    session.close()

    # ── PHASE 2 : ASSEMBLE INPUTS ────────────────────────────────────────────
    console.print()
    console.rule("[bold magenta]PHASE 2 — ASSEMBLE INPUTS[/bold magenta]", style="magenta")

    nhf_rate                         = Decimal(str(rules_jsonb.get("nhf", {}).get("rate", "0.025")))
    health_insurance_employee_amount = Decimal(str(rules_jsonb.get("health_insurance", {}).get("employee_monthly_amount", "0")))
    development_levy_amount          = Decimal(str(rules_jsonb.get("development_levy", {}).get("monthly_amount", "0")))
    life_insurance_employer_rate     = Decimal(str(rules_jsonb.get("life_insurance", {}).get("employer_rate", "0")))

    # Apply flat-amount client_component_metadata overrides (mirrors production payroll.py)
    if "DEVELOPMENT_LEVY" in client_overrides and "monthly_amount" in client_overrides["DEVELOPMENT_LEVY"]:
        development_levy_amount = Decimal(str(client_overrides["DEVELOPMENT_LEVY"]["monthly_amount"]))
    if "HEALTH_INSURANCE_EMPLOYEE" in client_overrides and "employee_monthly_amount" in client_overrides["HEALTH_INSURANCE_EMPLOYEE"]:
        health_insurance_employee_amount = Decimal(str(client_overrides["HEALTH_INSURANCE_EMPLOYEE"]["employee_monthly_amount"]))

    step(
        "context dict",
        "context = {\n"
        "    'tax_bands':                        tax_bands,\n"
        "    'pension_employee_rate':            pension_employee_rate,\n"
        "    'pension_employer_rate':            pension_employer_rate,\n"
        "    'rent_relief_cfg':                  rent_relief_cfg,\n"
        "    'nhf_rate':                         nhf_rate,\n"
        "    'health_insurance_employee_amount': health_insurance_employee_amount,\n"
        "    'development_levy_amount':          development_levy_amount,\n"
        "    'life_insurance_employer_rate':     life_insurance_employer_rate,\n"
        "    'employee_inputs':                  employee_inputs,\n"
        "    'client_meta':                      client_meta,\n"
        "    'payroll_rules':                    payroll_rules,\n"
        "    'period':                           period_ctx,\n"
        "    'historical_rule_sets':             [],\n"
        "    'historical_period_contexts':       {},\n"
        "    'current_rule_set_id':              current_rule_set_id,\n"
        "    'current_rule_set_effective_from':  None,\n"
        "}",
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
        "payroll_rules":                    payroll_rules,
        "period":                           period_ctx,
        "historical_rule_sets":             [],
        "historical_period_contexts":       {},
        "current_rule_set_id":              current_rule_set_id,
        "current_rule_set_effective_from":  None,
    }
    console.print(f"  [dim]pension_employee_rate = {context['pension_employee_rate']}[/dim]")
    console.print(f"  [dim]pension_employer_rate = {context['pension_employer_rate']}[/dim]")
    console.print(f"  [dim]rent_relief_cfg        = {rent_relief_cfg}[/dim]")
    console.print(f"  [dim]employee_inputs        = {len(employee_inputs)} input(s)[/dim]")
    console.print(f"  [dim]client_meta            = {len(client_meta)} component(s) (merged)[/dim]")
    console.print(f"  [dim]tax_bands              = {len(tax_bands)} band(s)[/dim]")
    console.print(f"  [dim]period                 = {period_ctx.period_start} → {period_ctx.period_end}  "
                  f"({period_ctx.period_type.value}, {period_ctx.working_days} working days)[/dim]")

    # ── PHASE 2.5 : PAYROLL RULES ─────────────────────────────────────────────
    console.print()
    console.rule("[bold magenta]PHASE 2.5 — PAYROLL RULES (apply_payroll_rules())[/bold magenta]", style="magenta")

    step(
        "apply_payroll_rules()",
        "from backend.domain.payroll.rule_evaluator import apply_payroll_rules\n"
        "\n"
        "# employee_inputs loaded from payroll_input (Step 10):\n"
        "#   {'regular_overtime_days': [{'quantity': 2, 'reference_date': date(...), ...}], ...}\n"
        "\n"
        "salary_components, rule_trace = apply_payroll_rules(\n"
        "    salary_components = salary_components,\n"
        "    payroll_rules     = payroll_rules,\n"
        "    employee_inputs   = employee_inputs,\n"
        "    client_meta       = client_meta,\n"
        ")",
    )
    salary_components, rule_trace = apply_payroll_rules(
        salary_components=salary_components,
        payroll_rules=payroll_rules,
        employee_inputs=employee_inputs,
        client_meta=client_meta,
        working_days=period_ctx.working_days,
        calendar_days=period_ctx.calendar_days,
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
    parser.add_argument("--workspace-id", default=None,
                        help="Workspace UUID (default: derived from employee record)")
    parser.add_argument("--period-start", default=None,
                        help="Pay period start date YYYY-MM-DD (default: first day of current month)")
    parser.add_argument("--period-end", default=None,
                        help="Pay period end date YYYY-MM-DD (default: last day of period_start's month)")
    args = parser.parse_args()
    run(args.employee_id, workspace_id=args.workspace_id,
        period_start=args.period_start, period_end=args.period_end)
