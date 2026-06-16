/**
 * Fetch wrapper with JWT auth and automatic token refresh.
 * On 401: refreshes once, retries. On second 401: clears tokens.
 *
 * All responses are deep-converted from snake_case → camelCase so
 * TypeScript interfaces (categoryId, ageGroup, …) match the API output.
 * Request bodies are sent as-is (snake_case), which is what Django expects.
 */
import { clearTokens, getStoredTokens, refreshAccessToken } from '@/lib/auth/auth-service';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.babymotion.app/api/v1';

function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function transformKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(transformKeys);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([k, v]) => [
        snakeToCamel(k),
        transformKeys(v),
      ])
    );
  }
  return value;
}

async function parseResponse<T>(res: Response): Promise<T> {
  if (res.status === 204) return undefined as T;
  const data = await res.json();
  return transformKeys(data) as T;
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit & { language?: string } = {}
): Promise<T> {
  const { language, ...fetchOptions } = options;
  const tokens = getStoredTokens();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(fetchOptions.headers as Record<string, string>),
    ...(tokens ? { Authorization: `Bearer ${tokens.access}` } : {}),
    ...(language ? { 'Accept-Language': language } : {}),
  };

  const res = await fetch(`${BASE_URL}${path}`, { ...fetchOptions, headers });

  if (res.status !== 401) {
    if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
    return parseResponse<T>(res);
  }

  // Attempt token refresh once
  const stored = getStoredTokens();
  if (!stored?.refresh) {
    clearTokens();
    throw new Error('Unauthorized');
  }

  const newTokens = await refreshAccessToken(stored.refresh);
  const retryRes = await fetch(`${BASE_URL}${path}`, {
    ...fetchOptions,
    headers: { ...headers, Authorization: `Bearer ${newTokens.access}` },
  });

  if (!retryRes.ok) {
    clearTokens();
    throw new Error('Unauthorized after refresh');
  }
  return parseResponse<T>(retryRes);
}
