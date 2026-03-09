const CHECKS = [
  { key: 'pay_cycle', label: 'Pay Cycle' },
  { key: 'grade', label: 'Grades' },
  { key: 'designation', label: 'Designations' },
  { key: 'salary_definition', label: 'Salary Definitions' },
  { key: 'payroll_rule', label: 'Payroll Rules' },
  { key: 'component_metadata', label: 'Component Metadata' },
];

interface Props {
  missing: string[];
  progressPercent: number;
}

export function ProgressChecklist({ missing, progressPercent }: Props) {
  const missingSet = new Set(missing);

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-slate-500 font-medium">Setup Progress</span>
        <span className="text-xs font-semibold text-slate-700">{progressPercent}%</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2 mb-4">
        <div
          className="h-2 rounded-full bg-green-500 transition-all"
          style={{ width: `${progressPercent}%` }}
        />
      </div>
      <ul className="space-y-1.5">
        {CHECKS.map(({ key, label }) => {
          const missing = missingSet.has(key);
          return (
            <li key={key} className="flex items-center gap-2 text-sm">
              {missing ? (
                <span className="w-4 h-4 rounded-full border-2 border-slate-300 shrink-0" />
              ) : (
                <svg className="w-4 h-4 text-green-500 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              )}
              <span className={missing ? 'text-slate-400' : 'text-slate-700'}>{label}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
