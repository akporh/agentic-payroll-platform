import { api } from './client';
import type {
  ValidateResponse,
  PreviewResponse,
  CommitResponse,
} from '../types/onboarding';

export const onboardingApi = {
  validate: (payload: unknown) =>
    api.post<ValidateResponse>('/onboarding/validate', payload),

  preview: (payload: unknown) =>
    api.post<PreviewResponse>('/onboarding/preview', payload),

  commit: (payload: unknown) =>
    api.post<CommitResponse>('/onboarding/commit', payload),
};
