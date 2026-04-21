/**
 * Design System — Barrel Export
 * Gate 2 deliverable: design tokens + coded component library
 *
 * Import from here in all Gate 3 screen files:
 *   import { Btn, StatusBadge, DataTable, ... } from '../design-system';
 *
 * Token CSS must be loaded via index.css (@import './design-system/tokens.css')
 */

// ── Actions — ACT-1 through ACT-6 ────────────────────────────────────────────
export { Btn, IconBtn, DownloadBtn } from './components/Actions';
export type { BtnProps, IconBtnProps, DownloadBtnProps } from './components/Actions';

// ── Status — STS-1 through STS-4 ─────────────────────────────────────────────
export { StatusBadge, AlertBanner, ProgressBar, SkeletonRow, SkeletonCard } from './components/Status';
export type {
  StatusBadgeProps,
  AlertBannerProps,
  ProgressBarProps,
  SkeletonRowProps,
  SkeletonCardProps,
  WorkspaceStatus,
  PayrollRunStatus,
  ReconciliationStatus,
  EmployeeStatus,
  ResultStatus,
  BadgeVariant,
} from './components/Status';

// ── Feedback — FBK-1 through FBK-4 ───────────────────────────────────────────
export { ToastProvider, useToast, InlineError, ConfirmDialog, EmptyState } from './components/Feedback';
export type {
  ToastVariant,
  ToastItem,
  InlineErrorProps,
  ConfirmDialogProps,
  EmptyStateProps,
} from './components/Feedback';

// ── Forms — FRM-1 through FRM-8 ──────────────────────────────────────────────
export {
  TextInput,
  NumberInput,
  SearchableSelect,
  DateInput,
  RadioGroup,
  Toggle,
  FileDropZone,
  Textarea,
} from './components/Forms';
export type {
  TextInputProps,
  NumberInputProps,
  SearchableSelectProps,
  SelectOption,
  DateInputProps,
  RadioGroupProps,
  RadioOption,
  ToggleProps,
  FileDropZoneProps,
  DropZoneState,
  TextareaProps,
} from './components/Forms';

// ── Data Display — DAT-1 through DAT-6 ───────────────────────────────────────
export {
  formatNaira,
  SummaryCard,
  SummaryCards,
  DataTable,
  ExpandableRow,
  ComponentTraceTable,
  ReconciliationCard,
  TimelineTable,
} from './components/DataDisplay';
export type {
  SummaryCardProps,
  SummaryCardsProps,
  Column,
  DataTableProps,
  SortDir,
  ExpandableRowProps,
  TraceEntry,
  ComponentTraceTableProps,
  ReconciliationCardProps,
  TimelineEntry,
  TimelineTableProps,
} from './components/DataDisplay';

// ── Navigation — NAV-1 through NAV-5 ─────────────────────────────────────────
export {
  TopBar,
  WorkspaceSidebar,
  Breadcrumb,
  TabBar,
  OnboardingStepper,
} from './components/Navigation';
export type {
  WorkspaceOption,
  TopBarProps,
  WorkspaceSidebarProps,
  SidebarSection,
  SidebarItem,
  BreadcrumbItem,
  BreadcrumbProps,
  Tab,
  TabBarProps,
  Step,
  StepState,
  OnboardingStepperProps,
} from './components/Navigation';

// ── Layout — LAY-1 through LAY-5 ─────────────────────────────────────────────
export {
  PageShell,
  ContentHeader,
  SlideOver,
  Modal,
  SplitPanel,
  Card,
} from './components/Layout';
export type {
  PageShellProps,
  ContentHeaderProps,
  SlideOverProps,
  ModalProps,
  SplitPanelProps,
  CardProps,
} from './components/Layout';
