// VITE_API_URL is the full base URL of the deployed backend (e.g. https://payroll-backend.onrender.com).
// In development it is left empty so Vite's dev-server proxy handles /api → localhost:8000/api/v1.
// In production (Vercel) set VITE_API_URL to the Render backend URL in the Vercel dashboard.
const VITE_API_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? '';
const BASE = `${VITE_API_URL}/api`;

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
