import { useState } from 'react';
import type { ExecutionTraceStep } from '../../types/payroll';
import { Card } from '../ui/Card';

interface Props {
  steps: ExecutionTraceStep[];
}

export function PayrollTimeline({ steps }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (steps.length === 0) {
    return (
      <Card title="Execution Timeline">
        <p className="text-sm text-slate-400 py-4 text-center">No trace data available for this run.</p>
      </Card>
    );
  }

  const errorCount = steps.filter((s) => s.status !== 'success').length;

  return (
    <Card
      title="Execution Timeline"
      action={
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">
            {steps.length} steps · {errorCount > 0 ? `${errorCount} error(s)` : 'all passed'}
          </span>
          <button
            onClick={() => setExpanded((v) => !v)}
            className="text-xs text-slate-500 hover:text-slate-700"
          >
            {expanded ? 'Collapse ▲' : 'Expand ▼'}
          </button>
        </div>
      }
    >
      {expanded ? (
        <ol className="space-y-0">
          {steps.map((step, i) => (
            <TimelineRow key={i} step={step} isLast={i === steps.length - 1} />
          ))}
        </ol>
      ) : (
        <p className="text-xs text-slate-400 text-center py-1">
          Click Expand to view execution steps
        </p>
      )}
    </Card>
  );
}

function TimelineRow({ step, isLast }: { step: ExecutionTraceStep; isLast: boolean }) {
  const success = step.status === 'success';

  return (
    <li className="flex gap-3">
      {/* Vertical connector */}
      <div className="flex flex-col items-center">
        <span
          className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
            success
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'
          }`}
        >
          {success ? '✓' : '✗'}
        </span>
        {!isLast && <span className="w-px flex-1 bg-slate-100 my-1" />}
      </div>

      {/* Step detail */}
      <div className={`pb-4 ${isLast ? '' : ''}`}>
        <p className={`text-sm font-medium ${success ? 'text-slate-800' : 'text-red-700'}`}>
          {formatStepName(step.step_name)}
        </p>

        <p className="text-xs text-slate-400 mt-0.5">
          {step.duration_ms != null ? `${step.duration_ms}ms` : '—'}
          {step.created_at && (
            <span className="ml-2">{new Date(step.created_at).toLocaleTimeString()}</span>
          )}
        </p>

        {step.error_message && (
          <p className="mt-1 text-xs text-red-500 font-mono bg-red-50 rounded px-2 py-1">
            {step.error_message}
          </p>
        )}
      </div>
    </li>
  );
}

/** Convert snake_case / "Batch process: N employees" labels to readable text. */
function formatStepName(name: string): string {
  return name;
}
