export interface ValidationError {
  field: string;
  message: string;
}

export interface ValidationWarning {
  field: string;
  message: string;
}

export interface ValidateResponse {
  status: 'valid' | 'invalid';
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface CommitResponse {
  status: 'success' | 'invalid' | 'error';
  message?: string;
  warnings?: string[];
  errors?: ValidationError[];
}

export interface HardValidation {
  status: 'PASS' | 'FAIL';
  errors: Array<{ category: string; message: string }>;
}

export interface AiReview {
  summary: string;
  warnings: string[];
  questions: string[];
  suggestions: string[];
}

export interface ReviewResult {
  hard_validation: HardValidation;
  ai_review: AiReview;
}
