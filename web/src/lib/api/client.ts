/**
 * Fetch wrapper with JWT auth and automatic token refresh.
 * On 401: refreshes once, retries. On second 401: clears tokens.
 */
import { clearTokens, getStoredTokens, refreshAccessToken } from '@/lib/auth/auth-service';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'https://api.babymotion.app/api/v1';

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
    return res.status === 204 ? (undefined as T) : res.json();
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
  return retryRes.status === 204 ? (undefined as T) : retryRes.json();
}
