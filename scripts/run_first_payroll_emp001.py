import sys
import os

# Make project root importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import uuid
from datetime import datetime
from decimal import Decimal

import psycopg2


def main():
    # =========================================================
    # PHASE 1.5 — FIRST REAL PAYROLL RUN (LOCAL ONLY)
    #
    # Loads:
    #   - Employee EMP001
    #   - Salary Definition components_jsonb
    #   - Payroll Rules rule_definition_json (rule_name)
    #
    # Executes:
    #   - Pure domain executor
    #
    # Persists:
    #   - payroll_result row
    # =========================================================


    print("\n==============================")
    print("PHASE 1.5 PAYROLL EXECUTION")
    print("==============================\n")

# =========================================================
# CONFIG
# =========================================================

DB_NAME = "payroll_dev"
DB_USER = "michaelemedo"
PAYROLL_YEAR = 2026
EMPLOYEE_NUMBER = "EMP001"

# =========================================================
# DB CONNECTION
# =========================================================

def get_connection():
    print("🔌 Connecting to Postgres...")
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        host="localhost",
        port=5432,   
 )


# =========================================================
# LOADERS
# =========================================================

def load_employee(cur):
    print("👤 Loading employee...")
    cur.execute("""
        SELECT employee_id
        FROM employee
        WHERE employee_number = %s
    """, (EMPLOYEE_NUMBER,))
    row = cur.fetchone()
    if not row:
        raise Exception("❌ Employee not found")
    print("   ✅ Employee found")
    return row[0]


def load_salary_definition(cur):
    print("💰 Loading salary definition...")
    cur.execute("""
        SELECT components_jsonb
        FROM salary_definition
        LIMIT 1
    """)
    row = cur.fetchone()
    if not row:
        raise Exception("❌ No salary definition found")
    print("   ✅ Salary template loaded")
    return row[0]


def adapt_components(components_dict):
    print("🔄 Adapting components to executor format...")
    return [
        {
            "code": code,
            "amount": Decimal(str(data.get("amount", 0)))
        }
        for code, data in components_dict.items()
    ]


def load_statutory_rule(cur):
    print(f"📜 Loading statutory rule for {PAYROLL_YEAR}...")
    cur.execute("""
        SELECT statutory_rule_id, version
        FROM statutory_rule
        WHERE version = %s
    """, (PAYROLL_YEAR,))
    row = cur.fetchone()
    if not row:
        raise Exception(f"❌ No statutory rule for year {PAYROLL_YEAR}")
    print("   ✅ Statutory regime located")
    return row[0], row[1]


def load_tax_bands(cur, statutory_rule_id):
    print("📊 Loading tax bands...")
    cur.execute("""
        SELECT lower_limit, upper_limit, rate
        FROM tax_band
        WHERE statutory_rule_id = %s
        ORDER BY lower_limit
    """, (statutory_rule_id,))
    rows = cur.fetchall()

    if not rows:
        raise Exception("❌ No tax bands found")

    print(f"   ✅ {len(rows)} tax bands loaded")

    return [
        {
            "lower_limit": Decimal(lower),
            "upper_limit": Decimal(upper) if upper is not None else None,
            "rate": Decimal(rate)
        }
        for lower, upper, rate in rows
    ]


def load_payroll_rule_ids(cur):
    print("🧾 Loading active payroll rules...")
    cur.execute("""
        SELECT rule_id
        FROM payroll_rule
        WHERE is_active = true
    """)
    rows = cur.fetchall()
    if not rows:
        raise Exception("❌ No active payroll rules found")
    print(f"   ✅ {len(rows)} rule(s) active")
    return [str(r[0]) for r in rows]


# =========================================================
# EXECUTION
# =========================================================

def main():
    print("\n===================================================")
    print("🚀 PHASE 1.5 — FIRST REAL PAYROLL EXECUTION")
    print("===================================================\n")

    conn = get_connection()
    cur = conn.cursor()

    payroll_run_id = str(uuid.uuid4())
    performed_by = "admin@acme.com"

    employee_id = load_employee(cur)
    components_dict = load_salary_definition(cur)
    components = adapt_components(components_dict)

    statutory_rule_id, statutory_version = load_statutory_rule(cur)
    tax_bands = load_tax_bands(cur, statutory_rule_id)
    payroll_rule_ids = load_payroll_rule_ids(cur)

    print("\n🧮 Executing payroll engine...\n")
    # 🔍 Debug: confirm which PAYE module Python is using
    import backend.domain.rules.paye as paye_module
    print("Loaded PAYE from:", paye_module.__file__)

    from backend.domain.payroll.executor import execute_single_employee_payroll

    result = execute_single_employee_payroll(
        payroll_run_id=payroll_run_id,
        employee_id=str(employee_id),
        components=components,
        tax_bands=tax_bands,
        statutory_rule_id=str(statutory_rule_id),
        statutory_version=statutory_version,
        payroll_rule_ids=payroll_rule_ids,
        performed_by=performed_by,
    )

    payroll_result = result["payroll_result"]

    print("===================================================")
    print("📄 PAYROLL PREVIEW")
    print("===================================================")
    print(f"💵 Gross Pay:        ₦{payroll_result['gross_pay']:,}")
    print(f"📉 Total Deductions: ₦{payroll_result['total_deductions']:,}")
    print(f"🏦 Net Pay:          ₦{payroll_result['net_pay']:,}")
    print("===================================================\n")

    # Persist result
    payroll_result_id = str(uuid.uuid4())

    print("💾 Persisting payroll_result to database...")

    cur.execute("""
        INSERT INTO payroll_result (
            payroll_result_id,
            payroll_run_id,
            employee_id,
            gross_components_jsonb,
            deductions_jsonb,
            net_pay,
            calculations_snapshot_json,
            created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        payroll_result_id,
        payroll_run_id,
        employee_id,
        json.dumps(payroll_result["gross_components"]),
        json.dumps(payroll_result["deductions"]),
        payroll_result["net_pay"],
        json.dumps(payroll_result["calculation_snapshot"]),
        datetime.utcnow()
    ))

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Payroll successfully written to DB")
    print(f"🆔 Payroll Result ID: {payroll_result_id}")
    print("\n🎉 PHASE 1 ACTIVATED — ACME PAYROLL IS LIVE\n")


if __name__ == "__main__":
    main()

