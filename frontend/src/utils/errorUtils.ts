export function extractError(e: unknown): string {
  if (e instanceof Error) {
    try {
      const parsed = JSON.parse(e.message.replace(/^\d+ [^:]+: /, ''));
      if (parsed?.detail) return String(parsed.detail);
    } catch { /* fall through */ }
    return e.message;
  }
  return 'An unexpected error occurred.';
}
