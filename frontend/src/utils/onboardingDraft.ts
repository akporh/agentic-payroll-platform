export type OnboardingDraftStep = 'client-config-json' | 'component-settings' | 'activate';

export interface OnboardingDraft {
  version: 1;
  workspaceId: string;
  savedAt: string;
  activeStep: OnboardingDraftStep;
  rawJson: string;
}

function draftKey(workspaceId: string): string {
  return `onboarding_draft_${workspaceId}`;
}

/**
 * Merge a partial patch into the stored draft and write it back.
 * Fails silently if localStorage is unavailable.
 */
export function saveDraft(workspaceId: string, patch: Partial<OnboardingDraft>): void {
  try {
    const existing = loadDraft(workspaceId) ?? {
      version: 1 as const,
      workspaceId,
      savedAt: new Date().toISOString(),
      activeStep: 'client-config-json' as OnboardingDraftStep,
      rawJson: '',
    };
    const updated: OnboardingDraft = {
      ...existing,
      ...patch,
      savedAt: new Date().toISOString(),
    };
    localStorage.setItem(draftKey(workspaceId), JSON.stringify(updated));
  } catch {
    // localStorage may be full or unavailable — degrade gracefully
  }
}

/**
 * Load the draft for a workspace.
 * Returns null if no draft exists or if the stored version is incompatible.
 */
export function loadDraft(workspaceId: string): OnboardingDraft | null {
  try {
    const raw = localStorage.getItem(draftKey(workspaceId));
    if (!raw) return null;
    const parsed = JSON.parse(raw) as OnboardingDraft;
    if (parsed.version !== 1) return null;
    return parsed;
  } catch {
    return null;
  }
}

/**
 * Remove the draft for a workspace.
 * Called after a successful onboarding commit.
 */
export function clearDraft(workspaceId: string): void {
  try {
    localStorage.removeItem(draftKey(workspaceId));
  } catch {
    // ignore
  }
}
