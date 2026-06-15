// Pure parsing utilities for native (client-format) Excel uploads.
// No React, no API calls — safe to import from any context.

export type AliasMap = Record<string, string[]>

export interface InputCodeDef {
  code: string;
  rule_name: string;
  category: string;
  calculation_method: string;
}

// ── Alias maps ────────────────────────────────────────────────────────────────

export const EMPLOYEE_ALIASES: AliasMap = {
  employee_id:    ['ID NUMBER', 'STAFF ID', 'EMPLOYEE ID', 'EMPLOYEE NO', 'EMPLOYEE NUMBER'],
  first_name:     ['FIRST NAME', 'FIRSTNAME', 'FORENAME'],
  last_name:      ['SURNAME', 'LAST NAME', 'FAMILY NAME'],
  grade:          ['CATEGORY', 'GRADE', 'STEP', 'GRADE CODE'],
  designation:    ['DESIGNATION', 'JOB TITLE', 'ROLE', 'POSITION'],
  tin:            ['TAX IDENTIFICATION', 'TIN', 'TAX ID'],
  rsa:            ['PENSION PIN', 'RSA PIN', 'RSA'],
  bank:           ['BANK', 'BANK NAME'],
  account_number: ['ACCOUNT NO', 'ACCOUNT NUMBER', 'ACCT NO'],
  contract_start: ['DATE EMPLOYED', 'START DATE', 'EMPLOYMENT DATE', 'JOINING DATE'],
  contract_end:   ['END DATE', 'CONTRACT END', 'EXIT DATE', 'TERMINATION DATE'],
}

export const PAYROLL_RECON_ALIASES: AliasMap = {
  employee_id:      ['ID NUMBER', 'STAFF ID', 'EMPLOYEE NO', 'EMPLOYEE NUMBER'],
  net_pay:          ['NET SALARY', 'NET PAY', 'NET', 'TAKE HOME'],
  gross_pay:        ['STAFF GROSS', 'GROSS SALARY', 'GROSS PAY', 'GROSS'],
  paye:             ['PAYE', 'TAX', 'INCOME TAX'],
  pension_employee: ['PENSION (EMPLOYEE)', 'PENSION EMPLOYEE', 'EMPLOYEE PENSION'],
  development_levy: ['DEVELOPMENT LEVY', 'DEV LEVY'],
  nhf:              ['NHF', 'NATIONAL HOUSING FUND'],
  basic_salary:     ['BASIC SALARY', 'BASIC', 'BASIC PAY'],
  housing:          ['HOUSING ALLOWANCE', 'HOUSING'],
  transport:        ['TRANSPORT ALLOWANCE', 'TRANSPORT'],
}

// ── Core functions ────────────────────────────────────────────────────────────

/** Score a row: count distinct target fields matched by cells in the row. */
export function scoreRow(row: unknown[], aliases: AliasMap): number {
  const matched = new Set<string>();
  for (const cell of row) {
    const normalized = String(cell ?? '').trim().toUpperCase();
    if (!normalized) continue;
    for (const [field, patterns] of Object.entries(aliases)) {
      if (patterns.some((p) => normalized === p || normalized.includes(p))) {
        matched.add(field);
      }
    }
  }
  return matched.size;
}

export interface DetectHeaderResult {
  rowIndex: number;
  confidence: number;
  mappings: Record<string, number>;
}

/** Scan first 15 rows, return best-scoring row index + confidence (alias-based). */
export function detectHeaderRow(
  rows: unknown[][],
  aliases: AliasMap,
): DetectHeaderResult {
  return detectHeaderRowByScorer(
    rows,
    (row) => scoreRow(row, aliases),
    (row) => buildColumnMap(row, aliases),
  );
}

/**
 * Scan first 15 rows using a custom scorer function.
 * Use when alias-based scoring doesn't apply (e.g. period input column detection).
 * Callers gate on `result.confidence >= minMatches` themselves.
 */
export function detectHeaderRowByScorer(
  rows: unknown[][],
  scoreFn: (row: string[]) => number,
  mappingsFn?: (row: string[]) => Record<string, number>,
): DetectHeaderResult {
  let best: DetectHeaderResult = { rowIndex: 0, confidence: 0, mappings: {} };
  const limit = Math.min(rows.length, 15);
  for (let i = 0; i < limit; i++) {
    // Score the RAW row so a single merged/title cell ("MARCH 2026 PAYROLL") that
    // forward-fills to every column doesn't score higher than a real header row
    // with several distinct input column names.
    const rawRow = rows[i].map((c) => String(c ?? '').trim());
    const score = scoreFn(rawRow);
    if (score > best.confidence) {
      // Forward-fill only for the mappings step, not for scoring
      const filledRow = forwardFillRow(rows[i]);
      best = {
        rowIndex: i,
        confidence: score,
        mappings: mappingsFn ? mappingsFn(filledRow) : {},
      };
    }
  }
  return best;
}

/** Forward-fill blanks in a header row (handles merged cells that export as empty). */
export function forwardFillRow(row: unknown[]): string[] {
  const result: string[] = [];
  let last = '';
  for (const cell of row) {
    const s = String(cell ?? '').trim();
    if (s) {
      last = s;
      result.push(s);
    } else {
      result.push(last);
    }
  }
  return result;
}

/** Map column indices to target fields using alias list (case-insensitive). */
export function buildColumnMap(headerRow: string[], aliases: AliasMap): Record<string, number> {
  const result: Record<string, number> = {};
  headerRow.forEach((cell, colIdx) => {
    const normalized = cell.trim().toUpperCase();
    if (!normalized) return;
    for (const [field, patterns] of Object.entries(aliases)) {
      if (result[field] !== undefined) continue; // first match wins
      if (patterns.some((p) => normalized === p || normalized.includes(p))) {
        result[field] = colIdx;
      }
    }
  });
  return result;
}

// ── Period input column header parsing ────────────────────────────────────────

const MONTHS: Record<string, string> = {
  JANUARY: '01', FEBRUARY: '02', MARCH: '03', APRIL: '04',
  MAY: '05', JUNE: '06', JULY: '07', AUGUST: '08',
  SEPTEMBER: '09', OCTOBER: '10', NOVEMBER: '11', DECEMBER: '12',
}

// Build month-name regexes once at module load — reused across all header parses
const MONTH_REGEXES: [RegExp, string][] = Object.entries(MONTHS).map(
  ([name, num]) => [new RegExp(`\\b${name}\\b`, 'g'), num],
)
const STRIP_PERIOD_WORDS_RE = /\b(THE|MONTH|OF|FOR|20\d{2,3})\b/g

export interface ParsedInputHeader {
  period: string | null;   // YYYY-MM
  keyword: string | null;
  amount: number | null;   // rate from @N300.00 — payroll rule amount used as quantity divisor
}

/**
 * Parse a period inputs column header like:
 * "THE MONTH OF JANUARY 2026 OVERTIME @ N1000.00"
 * → { period: "2026-01", keyword: "OVERTIME", amount: 1000 }
 *
 * The @AMOUNT encodes the payroll rule rate; quantity = cell_value / amount.
 */
export function parseInputColumnHeader(header: string): ParsedInputHeader {
  const upper = header.trim().toUpperCase();

  // Extract rate: @N300.00 / @₦300.00 / @5,000.00.00 (malformed) / @300 etc.
  // Capture uses ? (first decimal only → valid float); strip uses * (all decimals → full removal).
  const amountMatch = upper.match(/@\s*[N₦]?\s*([\d,]+(?:\.\d+)?)/);
  const amount = amountMatch ? parseFloat(amountMatch[1].replace(/,/g, '')) : null;

  // Strip @amount — * removes malformed "5,000.00.00" in full
  const normalized = upper.replace(/@\s*[N₦]?\s*[\d,]+(?:\.\d+)*/g, '').trim();

  // Drop end \b so a typo like "20206" still yields "2026" (5-digit word, no end boundary)
  const yearMatch = normalized.match(/\b(20\d{2})/);
  const year = yearMatch?.[1] ?? null;

  let monthNum: string | null = null;
  for (const [re, num] of MONTH_REGEXES) {
    re.lastIndex = 0;
    if (re.test(normalized)) {
      monthNum = num;
      break;
    }
  }

  const period = year && monthNum ? `${year}-${monthNum}` : null;

  // Strip period-related words in one pass, then strip month names
  let remainder = normalized.replace(STRIP_PERIOD_WORDS_RE, '');
  for (const [re] of MONTH_REGEXES) {
    re.lastIndex = 0; // reset stateful global regex
    remainder = remainder.replace(re, '');
  }
  const keyword = remainder.trim().replace(/\s+/g, ' ') || null;

  return { period, keyword, amount };
}

/** Score a row by how many cells look like period input column headers. */
export function scoreRowAsInputHeaders(row: unknown[]): number {
  let count = 0;
  for (const cell of row) {
    const { period, keyword } = parseInputColumnHeader(String(cell ?? ''));
    if (period && keyword) count++;
  }
  return count;
}

// ── Fuzzy token matching ──────────────────────────────────────────────────────

function levenshtein(a: string, b: string): number {
  const m = a.length, n = b.length;
  const dp: number[] = Array.from({ length: n + 1 }, (_, j) => j);
  for (let i = 1; i <= m; i++) {
    let prev = dp[0];
    dp[0] = i;
    for (let j = 1; j <= n; j++) {
      const temp = dp[j];
      dp[j] = a[i - 1] === b[j - 1] ? prev : 1 + Math.min(prev, dp[j], dp[j - 1]);
      prev = temp;
    }
  }
  return dp[n];
}

/** Tokens shorter than 4 chars require exact match; longer tokens allow up to 2 edits. */
function tokensMatch(a: string, b: string): boolean {
  if (a === b) return true;
  if (a.length < 4 || b.length < 4) return false;
  return levenshtein(a, b) <= 2;
}

/**
 * Subtype-aware fuzzy match: tokenise the keyword and each rule name/code, then score
 * by keyword coverage minus a penalty for extra tokens in the rule.
 *
 * "SPECIAL OVERTIME" correctly prefers special_overtime_days over overtime_days because
 * all keyword tokens hit the rule and it has fewer unmatched extras.
 * Plain "OVERTIME" scores equally against both variants (operator resolves in the mapping
 * panel) but never silently drops specificity the other way.
 *
 * Fuzzy token matching (Levenshtein ≤ 2, min length 4) handles common typos like
 * "WEEKDEND" → "WEEKEND" and truncations like "WEEKENE" → "WEEKEND".
 */
function computeMatchScore(kwTokens: string[], ruleTokens: string[]): number {
  const hits = kwTokens.filter((t) => ruleTokens.some((r) => tokensMatch(t, r))).length;
  const kwCoverage = hits / kwTokens.length;
  // Penalise rules that are more specific than the keyword (extra tokens not in keyword)
  const extra = ruleTokens.filter((t) => !kwTokens.some((k) => tokensMatch(k, t))).length;
  return kwCoverage - extra * 0.15;
}

export function matchInputCode(keyword: string, inputCodes: InputCodeDef[]): string | null {
  if (!keyword) return null;
  const kwTokens = keyword.toLowerCase().split(/\s+/).filter(Boolean);
  if (kwTokens.length === 0) return null;

  let best: { code: string; score: number } | null = null;

  for (const def of inputCodes) {
    const nameTokens = def.rule_name.toLowerCase().split(/[\s_-]+/).filter(Boolean);
    const codeTokens = def.code.toLowerCase().split(/[\s_-]+/).filter(Boolean);
    const score = Math.max(
      computeMatchScore(kwTokens, nameTokens),
      computeMatchScore(kwTokens, codeTokens),
    );
    if (score > 0 && (!best || score > best.score)) {
      best = { code: def.code, score };
    }
  }

  return best?.code ?? null;
}

// ── Date utility ──────────────────────────────────────────────────────────────

/** Convert a cell value (Date object or string) to ISO date string YYYY-MM-DD. */
export function toISODate(val: unknown): string {
  if (val instanceof Date) {
    const d = new Date(val.getTime() - val.getTimezoneOffset() * 60000);
    return d.toISOString().slice(0, 10);
  }
  const s = String(val ?? '').trim();
  if (!s) return '';
  // Handle Excel serial numbers (rare but possible)
  if (/^\d{5}$/.test(s)) {
    const d = new Date((parseInt(s) - 25569) * 86400 * 1000);
    return d.toISOString().slice(0, 10);
  }
  // Already ISO-ish
  const match = s.match(/^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$/);
  if (match) {
    return `${match[1]}-${match[2].padStart(2, '0')}-${match[3].padStart(2, '0')}`;
  }
  return s;
}
