const DEFAULT_BASE = "http://localhost:8000/api/v1";
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) || DEFAULT_BASE;
const TOKEN_KEY = "edunova_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export async function api<T>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(API_BASE + path, {
    method: options.method || "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (response.status === 204) {
    return null as T;
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      payload && payload.detail ? payload.detail : `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload as T;
}
