import { api } from './client';
import type {
  ValidateResponse,
  CommitResponse,
} from '../types/onboarding';

export const onboardingApi = {
  validate: (payload: unknown) =>
    api.post<ValidateResponse>('/onboarding/validate', payload),

  commit: (payload: unknown) =>
    api.post<CommitResponse>('/onboarding/commit', payload),
};
