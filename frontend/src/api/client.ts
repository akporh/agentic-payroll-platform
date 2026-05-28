// VITE_API_URL is intentionally left empty in production.
// Vercel rewrites /api/v1/* → Render backend, so no cross-origin requests are made.
// In development, Vite's dev-server proxy handles /api/v1 → localhost:8000/api/v1.
const VITE_API_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? '';
const BASE = `${VITE_API_URL}/api/v1`;

export class ApiError extends Error {
  response: { status: number };
  constructor(status: number, statusText: string, body: string) {
    super(`${status} ${statusText}: ${body}`);
    this.response = { status };
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(res.status, res.statusText, text);
  }
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
