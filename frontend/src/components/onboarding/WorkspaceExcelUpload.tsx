import { useRef, useState } from 'react';
import * as XLSX from 'xlsx';
import { Card } from '../ui/Card';
import { Btn } from '../ui/Btn';
import { AlertBox } from '../ui/AlertBox';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface WorkspaceConfig {
  workspace_id: string;
  structure: {
    pay_cycle: {
      frequency?: string;
      run_day?: number;
      cutoff_day?: number;
      payment_day?: number;
    };
    grades: { grade_code: string; description: string }[];
    designations: { designation_code: string; description: string }[];
    /** Optional per-component proration strategy overrides (6th sheet). */
    component_overrides: { component_code: string; proration_strategy?: string }[];
  };
  compensation: {
    salary_definitions: {
      name: string;
      code: string;
      components: Record<string, { amount: number }>;
    }[];
  };
  rules: {
    payroll_rules: {
      rule_name: string;
      rule_code: string;
      definition: Record<string, unknown>;
    }[];
  };
  /** Optional workspace payroll config from 7th sheet. */
  workspace_payroll_config?: {
    ph_mode?: string;
    saturday_ph_rule?: string;
    sunday_ph_rule?: string;
    d3_leave_overlap_rule?: string;
    d4_absence_rule?: string;
  };
}

interface Props {
  workspaceId: string;
  onConfigParsed: (config: WorkspaceConfig) => void;
}

// ── Required columns per sheet ────────────────────────────────────────────────

const SALARY_COMPONENT_COLS = ['BASIC', 'HOUSING', 'TRANSPORT'] as const;

// ── Template generation ───────────────────────────────────────────────────────

function downloadTemplate() {
  const wb = XLSX.utils.book_new();

  // Pay Cycle
  const payCycleData = [
    { frequency: 'monthly', run_day: 25, cutoff_day: 20, payment_day: 28 },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(payCycleData), 'Pay Cycle');

  // Grades
  const gradesData = [
    { grade_code: 'G1', description: 'Grade 1 - Entry Level' },
    { grade_code: 'G2', description: 'Grade 2 - Mid Level' },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(gradesData), 'Grades');

  // Designations
  const designationsData = [
    { designation_code: 'ENGINEER', description: 'Software Engineer' },
    { designation_code: 'ANALYST', description: 'Business Analyst' },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(designationsData), 'Designations');

  // Salary Definitions
  const salaryDefsData = [
    {
      name: 'Engineer Grade 1',
      code: 'ENGINEER_G1',
      BASIC: 200000,
      HOUSING: 80000,
      TRANSPORT: 40000,
      CONSOLIDATED_ALLOWANCE: 0,
    },
    {
      name: 'Analyst Grade 2',
      code: 'ANALYST_G2',
      BASIC: 250000,
      HOUSING: 100000,
      TRANSPORT: 50000,
      CONSOLIDATED_ALLOWANCE: 0,
    },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(salaryDefsData), 'Salary Definitions');

  // Payroll Rules
  // Rule Type must be one of: Unit × Rate | Daily Rate Deduction | Fixed Amount | OT Multiplier
  //   Unit × Rate         — requires: input_field, rate  (e.g. overtime_days × rate)
  //   Daily Rate Deduction — requires: input_field        (e.g. absent_days deducted from salary)
  //   Fixed Amount         — requires: amount             (e.g. flat bonus, optionally with condition)
  //   OT Multiplier        — requires: input_field, rate_code (e.g. OT1 hours × basic_hourly × 1.5)
  const rulesData = [
    {
      rule_name:   'OVERTIME_PAY',
      rule_type:   'Unit × Rate',
      input_field: 'overtime_days',
      rate:        5000,
      unit:        'days',
    },
    {
      rule_name:   'Absence Deduction',
      rule_type:   'Daily Rate Deduction',
      input_field: 'absent_days',
    },
    {
      rule_name:   'OT1 - Weekday Overtime',
      rule_type:   'OT Multiplier',
      input_field: 'ot1_hours',
      rate_code:   'OT001',
    },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(rulesData), 'Payroll Rules');

  // Component Overrides (optional — leave blank to use global defaults)
  const componentOverridesData = [
    { component_code: 'BASIC',     proration_strategy: 'work_days' },
    { component_code: 'HOUSING',   proration_strategy: 'calendar_days' },
    { component_code: 'TRANSPORT', proration_strategy: 'calendar_days' },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(componentOverridesData), 'Component Overrides');

  // Workspace Payroll Config (optional 7th sheet — one row only)
  const wpcData = [
    {
      ph_mode:              'AUTOMATIC',
      saturday_ph_rule:     'PH_TAKES_PRECEDENCE',
      sunday_ph_rule:       'PH_TAKES_PRECEDENCE',
      d3_leave_overlap_rule:'LEAVE_ABSORBS_PH',
      d4_absence_rule:      'ABSENT_IS_DEDUCTIBLE',
    },
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(wpcData), 'Workspace Payroll Config');

  XLSX.writeFile(wb, 'workspace_config_template.xlsx');
}

// ── Parse logic ───────────────────────────────────────────────────────────────

function normaliseRow(row: Record<string, unknown>): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(row)) {
    out[k.trim()] = v;
  }
  return out;
}

function parseWorkbook(
  workbook: XLSX.WorkBook,
  workspaceId: string,
): { config: WorkspaceConfig | null; errors: string[]; warnings: string[] } {
  const errors: string[] = [];
  const warnings: string[] = [];

  // ── Validate required sheets ──────────────────────────────────────────────
  const requiredSheets = ['Pay Cycle', 'Grades', 'Designations', 'Salary Definitions', 'Payroll Rules'];
  for (const sheet of requiredSheets) {
    if (!workbook.Sheets[sheet]) {
      errors.push(`Missing required sheet: "${sheet}"`);
    }
  }
  if (errors.length > 0) return { config: null, errors, warnings };

  // ── Pay Cycle ─────────────────────────────────────────────────────────────
  const payCycleRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
    workbook.Sheets['Pay Cycle'],
    { defval: '' },
  ).map(normaliseRow);

  const rawPc = payCycleRows[0] ?? {};
  const pay_cycle = {
    frequency: String(rawPc['frequency'] ?? '').trim() || undefined,
    run_day: rawPc['run_day'] !== '' ? Number(rawPc['run_day']) : undefined,
    cutoff_day: rawPc['cutoff_day'] !== '' ? Number(rawPc['cutoff_day']) : undefined,
    payment_day: rawPc['payment_day'] !== '' ? Number(rawPc['payment_day']) : undefined,
  };

  // ── Grades ────────────────────────────────────────────────────────────────
  const gradesRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
    workbook.Sheets['Grades'],
    { defval: '' },
  ).map(normaliseRow);

  if (gradesRows.length === 0 || !Object.prototype.hasOwnProperty.call(gradesRows[0], 'grade_code')) {
    errors.push('Sheet "Grades" is missing required column: grade_code');
  }
  const grades = gradesRows
    .filter((r) => String(r['grade_code'] ?? '').trim())
    .map((r) => ({
      grade_code: String(r['grade_code']).trim(),
      description: String(r['description'] ?? '').trim(),
    }));

  // ── Designations ──────────────────────────────────────────────────────────
  const desigRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
    workbook.Sheets['Designations'],
    { defval: '' },
  ).map(normaliseRow);

  if (desigRows.length === 0 || !Object.prototype.hasOwnProperty.call(desigRows[0], 'designation_code')) {
    errors.push('Sheet "Designations" is missing required column: designation_code');
  }
  const designations = desigRows
    .filter((r) => String(r['designation_code'] ?? '').trim())
    .map((r) => ({
      designation_code: String(r['designation_code']).trim(),
      description: String(r['description'] ?? '').trim(),
    }));

  // ── Salary Definitions ────────────────────────────────────────────────────
  const salaryRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
    workbook.Sheets['Salary Definitions'],
    { defval: '' },
  ).map(normaliseRow);

  if (salaryRows.length > 0) {
    const firstKeys = Object.keys(salaryRows[0]);
    const missingCols = (['name', 'code', ...SALARY_COMPONENT_COLS] as string[]).filter(
      (c) => !firstKeys.includes(c),
    );
    if (missingCols.length > 0) {
      errors.push(`Sheet "Salary Definitions" is missing columns: ${missingCols.join(', ')}`);
    }
  }

  const salary_definitions = salaryRows
    .filter((r) => String(r['name'] ?? '').trim())
    .map((r, i) => {
      const name = String(r['name']).trim();
      if (!name) {
        errors.push(`Salary Definitions row ${i + 2}: name is empty`);
      }
      // Build components from all numeric columns except name and code
      const components: Record<string, { amount: number }> = {};
      for (const [k, v] of Object.entries(r)) {
        if (k === 'name' || k === 'code') continue;
        const amount = Number(v);
        if (!isNaN(amount) && amount !== 0) {
          components[k] = { amount };
        }
      }
      return {
        name,
        code: String(r['code'] ?? '').trim() || name.toUpperCase().replace(/\s+/g, '_'),
        components,
      };
    });

  // ── Payroll Rules ─────────────────────────────────────────────────────────
  const rulesRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
    workbook.Sheets['Payroll Rules'],
    { defval: '' },
  ).map(normaliseRow);

  const RULE_TYPE_MAP: Record<string, string> = {
    'unit × rate':           'unit_multiplier',
    'daily rate deduction':  'daily_rate_deduction',
    'fixed amount':          'fixed_amount',
    'ot multiplier':         'ot_multiplier',
  };
  function resolveCalculationMethod(ruleType: string): string {
    return RULE_TYPE_MAP[ruleType.toLowerCase().trim()] ?? ruleType;
  }

  const payroll_rules = rulesRows
    .filter((r) => String(r['rule_name'] ?? '').trim())
    .map((r) => {
      const { rule_name, rule_code, ...rest } = r;
      // Everything except rule_name and rule_code goes into definition.
      // rule_type (user-friendly) is mapped back to calculation_method (technical).
      const definition: Record<string, unknown> = {};
      for (const [k, v] of Object.entries(rest)) {
        if (v !== '' && v != null) {
          if (k === 'rule_type') {
            definition['calculation_method'] = resolveCalculationMethod(String(v));
          } else if (k === 'ot_code' && !definition['rate_code']) {
            definition['rate_code'] = v;
          } else {
            definition[k] = v;
          }
        }
      }
      return {
        rule_name: String(rule_name ?? '').trim(),
        rule_code: String(rule_code ?? '').trim(),
        definition,
      };
    });

  // Warn on ot_multiplier rules missing rate_code — rule will fail at runtime
  payroll_rules.forEach((rule, i) => {
    const method = rule.definition['calculation_method'];
    if (method === 'ot_multiplier' && !rule.definition['rate_code']) {
      warnings.push(
        `Payroll Rules row ${i + 2} ("${rule.rule_name}"): ot_multiplier rule has no rate_code — rule will fail at runtime.`,
      );
    }
  });

  // ── Component Overrides (optional 6th sheet) ──────────────────────────
  const VALID_STRATEGIES = new Set(['work_days', 'calendar_days', 'fixed_30']);
  const component_overrides: { component_code: string; proration_strategy?: string }[] = [];

  if (workbook.Sheets['Component Overrides']) {
    const overrideRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
      workbook.Sheets['Component Overrides'],
      { defval: '' },
    ).map(normaliseRow);

    overrideRows
      .filter((r) => String(r['component_code'] ?? '').trim())
      .forEach((r, i) => {
        const code     = String(r['component_code']).trim().toUpperCase();
        const strategy = String(r['proration_strategy'] ?? '').trim().toLowerCase();
        if (strategy && !VALID_STRATEGIES.has(strategy)) {
          errors.push(
            `Component Overrides row ${i + 2}: proration_strategy '${strategy}' is invalid. ` +
            `Use work_days, calendar_days, or fixed_30.`,
          );
          return;
        }
        component_overrides.push({ component_code: code, proration_strategy: strategy || undefined });
      });
  }

  // ── Workspace Payroll Config (optional 7th sheet) ────────────────────────
  let workspace_payroll_config: WorkspaceConfig['workspace_payroll_config'];
  if (workbook.Sheets['Workspace Payroll Config']) {
    const wpcRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(
      workbook.Sheets['Workspace Payroll Config'],
      { defval: '' },
    ).map(normaliseRow);
    if (wpcRows.length > 0) {
      const wpc = wpcRows[0];
      const phMode = String(wpc['ph_mode'] ?? '').trim().toUpperCase();
      if (phMode && !['AUTOMATIC', 'FILE_BASED'].includes(phMode)) {
        warnings.push(`Workspace Payroll Config: ph_mode '${phMode}' is not valid. Use AUTOMATIC or FILE_BASED.`);
      }
      workspace_payroll_config = {
        ph_mode:               phMode || undefined,
        saturday_ph_rule:      String(wpc['saturday_ph_rule'] ?? '').trim() || undefined,
        sunday_ph_rule:        String(wpc['sunday_ph_rule'] ?? '').trim() || undefined,
        d3_leave_overlap_rule: String(wpc['d3_leave_overlap_rule'] ?? '').trim() || undefined,
        d4_absence_rule:       String(wpc['d4_absence_rule'] ?? '').trim() || undefined,
      };
    }
  }

  if (errors.length > 0) return { config: null, errors, warnings };

  return {
    config: {
      workspace_id: workspaceId,
      structure: { pay_cycle, grades, designations, component_overrides },
      compensation: { salary_definitions },
      rules: { payroll_rules },
      workspace_payroll_config,
    },
    errors: [],
    warnings,
  };
}

// ── Component ─────────────────────────────────────────────────────────────────

export function WorkspaceExcelUpload({ workspaceId, onConfigParsed }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [parseErrors, setParseErrors] = useState<string[]>([]);
  const [parseWarnings, setParseWarnings] = useState<string[]>([]);
  const [fileName, setFileName] = useState<string | null>(null);
  const [parsedConfig, setParsedConfig] = useState<WorkspaceConfig | null>(null);
  const [jsonOpen, setJsonOpen] = useState(false);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setParseErrors([]);
    setParseWarnings([]);
    setParsedConfig(null);
    setJsonOpen(false);

    const reader = new FileReader();
    reader.onload = (ev) => {
      try {
        const workbook = XLSX.read(ev.target?.result, { type: 'array' });
        const { config, errors, warnings } = parseWorkbook(workbook, workspaceId);
        if (errors.length > 0) {
          setParseErrors(errors);
          return;
        }
        if (warnings.length > 0) setParseWarnings(warnings);
        if (config) {
          setParsedConfig(config);
          onConfigParsed(config);
        }
      } catch {
        setParseErrors(['Failed to read file. Ensure it is a valid .xlsx file.']);
      }
    };
    reader.readAsArrayBuffer(file);
    e.target.value = '';
  }

  const gradeCount          = parsedConfig?.structure.grades.length ?? 0;
  const designationCount    = parsedConfig?.structure.designations.length ?? 0;
  const salaryDefCount      = parsedConfig?.compensation.salary_definitions.length ?? 0;
  const ruleCount           = parsedConfig?.rules.payroll_rules.length ?? 0;
  const overrideCount       = parsedConfig?.structure.component_overrides.length ?? 0;

  return (
    <Card title="Upload Workspace Config from Excel">
      <p className="text-xs text-slate-500 mb-3">
        Download the template, fill in your pay cycle, grades, designations, salary definitions, and payroll rules,
        then upload the completed file.
      </p>

      {/* Download template */}
      <div className="mb-4">
        <Btn variant="secondary" onClick={downloadTemplate}>
          ↓ Download Template
        </Btn>
        <p className="text-xs text-slate-400 mt-1.5">
          5 required sheets + 2 optional: Pay Cycle · Grades · Designations · Salary Definitions · Payroll Rules · Component Overrides · Workspace Payroll Config
        </p>
      </div>

      {/* Upload zone */}
      <div className="flex items-center gap-3 mb-3">
        <input
          ref={fileInputRef}
          type="file"
          accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          onChange={handleFile}
          className="hidden"
        />
        <Btn variant="secondary" onClick={() => fileInputRef.current?.click()}>
          Choose File
        </Btn>
        {fileName && (
          <span className="text-xs text-slate-500 truncate max-w-xs">{fileName}</span>
        )}
      </div>

      {/* Parse errors */}
      {parseErrors.length > 0 && (
        <div className="mb-3">
          <AlertBox type="error" title="Parse Errors" messages={parseErrors} />
        </div>
      )}

      {/* Parse warnings (non-blocking) */}
      {parseWarnings.length > 0 && (
        <div className="mb-3">
          <AlertBox type="warning" title="Warnings" messages={parseWarnings} />
        </div>
      )}

      {/* Success summary */}
      {parsedConfig && parseErrors.length === 0 && (
        <div className="mb-3 space-y-2">
          <AlertBox
            type="success"
            messages={[
              `Parsed: ${gradeCount} grade${gradeCount !== 1 ? 's' : ''}, ` +
              `${designationCount} designation${designationCount !== 1 ? 's' : ''}, ` +
              `${salaryDefCount} salary definition${salaryDefCount !== 1 ? 's' : ''}, ` +
              `${ruleCount} payroll rule${ruleCount !== 1 ? 's' : ''}` +
              (overrideCount > 0 ? `, ${overrideCount} component override${overrideCount !== 1 ? 's' : ''}` : '') +
              `.`,
            ]}
          />

          {/* Collapsible JSON preview */}
          <div className="border border-slate-200 rounded-lg">
            <button
              className="w-full flex items-center justify-between px-4 py-2.5 text-left"
              onClick={() => setJsonOpen((v) => !v)}
            >
              <span className="text-xs font-semibold text-slate-600">Generated JSON</span>
              <span className="text-xs text-slate-400 ml-2">{jsonOpen ? '▲ Hide' : '▼ Show'}</span>
            </button>
            {jsonOpen && (
              <pre className="bg-slate-50 text-slate-700 text-xs rounded-b-lg p-4 overflow-auto max-h-64 whitespace-pre-wrap border-t border-slate-200">
                {JSON.stringify(parsedConfig, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </Card>
  );
}
