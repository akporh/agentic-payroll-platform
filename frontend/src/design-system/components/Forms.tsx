/**
 * Forms — FRM-1 through FRM-8
 *
 * TextInput       FRM-1 — labelled text input, all states
 * NumberInput     FRM-2 — numeric / currency input
 * SearchableSelect FRM-3 — grouped option dropdown (input codes group by category)
 * DateInput       FRM-4 — date picker (date-only + month-only variants)
 * RadioGroup      FRM-5 — single-choice with descriptions
 * Toggle          FRM-6 — inline active/inactive toggle
 * FileDropZone    FRM-7 — drag-and-drop upload
 * Textarea        FRM-8 — multi-line text
 *
 * Rules (ux-designer + ui-designer):
 * - Every input has a VISIBLE label above — never placeholder-only
 * - Label-to-input gap: 4px (var(--gap-label-input))
 * - Between form fields: 16px+ (must exceed label-to-input gap)
 * - Heights match button scale: sm=32px md=40px lg=48px
 * - Error messages appear on blur, not keystroke
 * - DD-6: Input code dropdown groups by category (EARNING/DEDUCTION/INFORMATION)
 */

import React, { useId, useRef, useState } from 'react';
import { InlineError } from './Feedback';

// ── Shared label + wrapper ────────────────────────────────────────────────────

interface FieldWrapperProps {
  label: string;
  required?: boolean;
  error?: string;
  hint?: string;
  id: string;
  children: React.ReactNode;
  className?: string;
}

function FieldWrapper({ label, required, error, hint, id, children, className = '' }: FieldWrapperProps) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <label htmlFor={id} className="text-sm font-medium text-gray-700">
        {label}
        {required && <span className="ml-0.5 text-red-500" aria-hidden="true">*</span>}
      </label>
      {children}
      {hint && !error && <p className="text-xs text-gray-500">{hint}</p>}
      {error && <InlineError id={`${id}-error`} message={error} />}
    </div>
  );
}

const inputBase =
  'w-full border text-sm text-gray-900 bg-white placeholder-gray-400 ' +
  'focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent ' +
  'disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed ' +
  'transition-colors';

const inputError = 'border-red-400 focus:ring-red-500';
const inputDefault = 'border-gray-300 hover:border-gray-400';

// ── FRM-1 — Text Input ────────────────────────────────────────────────────────

export interface TextInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label: string;
  error?: string;
  hint?: string;
  /** Optional content rendered inside the input's right side */
  suffix?: React.ReactNode;
}

export function TextInput({ label, error, hint, required, disabled, suffix, className = '', ...props }: TextInputProps) {
  const id = useId();

  return (
    <FieldWrapper label={label} required={required} error={error} hint={hint} id={id} className={className}>
      <div className="relative">
        <input
          id={id}
          required={required}
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          style={{ borderRadius: 'var(--radius-input)', height: 'var(--height-md)' }}
          className={`${inputBase} ${error ? inputError : inputDefault} px-3 ${suffix ? 'pr-10' : ''}`}
          {...props}
        />
        {suffix && (
          <span className="absolute inset-y-0 right-3 flex items-center text-sm text-gray-500 pointer-events-none">
            {suffix}
          </span>
        )}
      </div>
    </FieldWrapper>
  );
}

// ── FRM-2 — Number Input ──────────────────────────────────────────────────────

export interface NumberInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id' | 'type'> {
  label: string;
  /** Show ₦ prefix for currency inputs */
  currency?: boolean;
  error?: string;
  hint?: string;
}

export function NumberInput({ label, currency, error, hint, required, disabled, className = '', ...props }: NumberInputProps) {
  const id = useId();

  return (
    <FieldWrapper label={label} required={required} error={error} hint={hint} id={id} className={className}>
      <div className="relative">
        {currency && (
          <span className="absolute inset-y-0 left-3 flex items-center text-sm text-gray-500 pointer-events-none select-none">
            ₦
          </span>
        )}
        <input
          id={id}
          type="number"
          required={required}
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          style={{
            borderRadius: 'var(--radius-input)',
            height: 'var(--height-md)',
            fontVariantNumeric: 'var(--font-numeric)',
          }}
          className={`${inputBase} ${error ? inputError : inputDefault} ${currency ? 'pl-7' : 'pl-3'} pr-3`}
          {...props}
        />
      </div>
    </FieldWrapper>
  );
}

// ── FRM-3 — Searchable Select ─────────────────────────────────────────────────

export interface SelectOption {
  value: string;
  label: string;
  group?: string;
}

export interface SearchableSelectProps {
  label: string;
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

export function SearchableSelect({
  label,
  options,
  value,
  onChange,
  placeholder = 'Select…',
  error,
  hint,
  required,
  disabled,
  className = '',
}: SearchableSelectProps) {
  const id = useId();

  /* Group options by `group` key — DD-6 */
  const grouped = options.reduce<Record<string, SelectOption[]>>((acc, opt) => {
    const g = opt.group ?? '__ungrouped__';
    if (!acc[g]) acc[g] = [];
    acc[g].push(opt);
    return acc;
  }, {});

  const groups = Object.entries(grouped);
  const hasGroups = groups.some(([g]) => g !== '__ungrouped__');

  return (
    <FieldWrapper label={label} required={required} error={error} hint={hint} id={id} className={className}>
      <div className="relative">
        <select
          id={id}
          value={value}
          disabled={disabled}
          required={required}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
          onChange={(e) => onChange?.(e.target.value)}
          style={{ borderRadius: 'var(--radius-input)', height: 'var(--height-md)' }}
          className={`${inputBase} ${error ? inputError : inputDefault} pl-3 pr-9 appearance-none cursor-pointer`}
        >
          <option value="" disabled>{placeholder}</option>
          {hasGroups
            ? groups.map(([group, opts]) =>
                group === '__ungrouped__' ? (
                  opts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)
                ) : (
                  <optgroup key={group} label={group}>
                    {opts.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </optgroup>
                ),
              )
            : options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        {/* Chevron icon */}
        <span className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-gray-400">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </span>
      </div>
    </FieldWrapper>
  );
}

// ── FRM-4 — Date Input ────────────────────────────────────────────────────────

export interface DateInputProps {
  label: string;
  value?: string;
  onChange?: (value: string) => void;
  /** 'month' shows YYYY-MM picker, 'date' shows YYYY-MM-DD */
  mode?: 'date' | 'month';
  min?: string;
  max?: string;
  error?: string;
  hint?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

export function DateInput({ label, value, onChange, mode = 'date', min, max, error, hint, required, disabled, className = '' }: DateInputProps) {
  const id = useId();

  return (
    <FieldWrapper label={label} required={required} error={error} hint={hint} id={id} className={className}>
      <input
        id={id}
        type={mode}
        value={value}
        min={min}
        max={max}
        required={required}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        onChange={(e) => onChange?.(e.target.value)}
        style={{ borderRadius: 'var(--radius-input)', height: 'var(--height-md)' }}
        className={`${inputBase} ${error ? inputError : inputDefault} px-3`}
      />
    </FieldWrapper>
  );
}

// ── FRM-5 — Radio Group ───────────────────────────────────────────────────────

export interface RadioOption {
  value: string;
  label: string;
  description?: string;
}

export interface RadioGroupProps {
  label: string;
  name: string;
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  required?: boolean;
  className?: string;
}

export function RadioGroup({ label, name, options, value, onChange, error, required, className = '' }: RadioGroupProps) {
  const groupId = useId();

  return (
    <fieldset className={className}>
      <legend className="text-sm font-medium text-gray-700 mb-2">
        {label}
        {required && <span className="ml-0.5 text-red-500" aria-hidden="true">*</span>}
      </legend>
      <div className="flex flex-col gap-2">
        {options.map((opt) => {
          const id = `${groupId}-${opt.value}`;
          const checked = value === opt.value;
          return (
            <label
              key={opt.value}
              htmlFor={id}
              style={{ borderRadius: 'var(--radius-input)' }}
              className={`flex items-start gap-3 p-3 border cursor-pointer transition-colors ${
                checked
                  ? 'border-brand bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 bg-white'
              }`}
            >
              <input
                id={id}
                type="radio"
                name={name}
                value={opt.value}
                checked={checked}
                required={required}
                onChange={() => onChange?.(opt.value)}
                className="mt-0.5 h-4 w-4 text-brand border-gray-300 focus:ring-brand focus:ring-offset-1"
              />
              <div>
                <p className="text-sm font-medium text-gray-900">{opt.label}</p>
                {opt.description && <p className="mt-0.5 text-xs text-gray-500">{opt.description}</p>}
              </div>
            </label>
          );
        })}
      </div>
      {error && <InlineError message={error} className="mt-2" />}
    </fieldset>
  );
}

// ── FRM-6 — Toggle ────────────────────────────────────────────────────────────

export interface ToggleProps {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  /** Show label to the right of the toggle */
  inlineLabel?: boolean;
  className?: string;
}

export function Toggle({ label, checked, onChange, disabled, inlineLabel = false, className = '' }: ToggleProps) {
  const id = useId();

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {!inlineLabel && <label htmlFor={id} className="text-sm font-medium text-gray-700">{label}</label>}
      <button
        id={id}
        role="switch"
        type="button"
        aria-checked={checked}
        aria-label={inlineLabel ? label : undefined}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        style={{ transition: 'background-color var(--transition-normal)' }}
        className={[
          'relative inline-flex h-6 w-11 shrink-0 items-center rounded-full',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2',
          'disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer',
          checked ? 'bg-green-500' : 'bg-gray-200',
        ].join(' ')}
      >
        <span
          style={{ transition: 'transform var(--transition-normal)' }}
          className={`inline-block h-4 w-4 rounded-full bg-white shadow-sm transform ${checked ? 'translate-x-6' : 'translate-x-1'}`}
        />
      </button>
      {inlineLabel && <label htmlFor={id} className="text-sm text-gray-700 cursor-pointer">{label}</label>}
    </div>
  );
}

// ── FRM-7 — File Drop Zone ────────────────────────────────────────────────────

export type DropZoneState = 'idle' | 'drag-over' | 'processing' | 'success' | 'error';

export interface FileDropZoneProps {
  accept?: string;
  label?: string;
  hint?: string;
  state?: DropZoneState;
  errorMessage?: string;
  successMessage?: string;
  onFile: (file: File) => void;
  className?: string;
}

export function FileDropZone({ accept, label = 'Drop file here or click to browse', hint, state = 'idle', errorMessage, successMessage, onFile, className = '' }: FileDropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) onFile(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFile(file);
  };

  const isActive = isDragging || state === 'drag-over';

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{ borderRadius: 'var(--radius-card)', transition: 'all var(--transition-fast)' }}
      className={[
        'flex flex-col items-center justify-center gap-3 p-8 border-2 border-dashed cursor-pointer',
        isActive ? 'border-brand bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-gray-400',
        state === 'success' ? 'border-green-400 bg-green-50' : '',
        state === 'error' ? 'border-red-400 bg-red-50' : '',
        state === 'processing' ? 'pointer-events-none' : '',
        className,
      ].join(' ')}
      role="button"
      tabIndex={0}
      aria-label={label}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click(); }}
    >
      <input ref={inputRef} type="file" accept={accept} className="sr-only" onChange={handleChange} tabIndex={-1} />
      {state === 'processing' && (
        <svg className="w-8 h-8 text-blue-500 animate-spin" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
        </svg>
      )}
      {state === 'success' && (
        <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )}
      {state === 'error' && (
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )}
      {(state === 'idle' || state === 'drag-over') && (
        <svg className={`w-8 h-8 ${isActive ? 'text-brand' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
      )}
      <div className="text-center">
        {state === 'success' && <p className="text-sm font-medium text-green-700">{successMessage ?? 'File uploaded'}</p>}
        {state === 'error' && <p className="text-sm font-medium text-red-700">{errorMessage ?? 'Upload failed — try again'}</p>}
        {state === 'processing' && <p className="text-sm font-medium text-blue-700">Processing…</p>}
        {(state === 'idle' || state === 'drag-over') && (
          <>
            <p className="text-sm font-medium text-gray-700">{label}</p>
            {hint && <p className="mt-0.5 text-xs text-gray-500">{hint}</p>}
          </>
        )}
      </div>
    </div>
  );
}

// ── FRM-8 — Textarea ──────────────────────────────────────────────────────────

export interface TextareaProps
  extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'id'> {
  label: string;
  error?: string;
  hint?: string;
}

export function Textarea({ label, error, hint, required, disabled, className = '', ...props }: TextareaProps) {
  const id = useId();

  return (
    <FieldWrapper label={label} required={required} error={error} hint={hint} id={id} className={className}>
      <textarea
        id={id}
        required={required}
        disabled={disabled}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
        style={{ borderRadius: 'var(--radius-input)' }}
        className={[
          inputBase,
          error ? inputError : inputDefault,
          'px-3 py-2 min-h-[100px] resize-y',
        ].join(' ')}
        {...props}
      />
    </FieldWrapper>
  );
}
