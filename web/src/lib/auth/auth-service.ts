/**
 * Shared auth logic — token storage, exchange, and refresh.
 * Works in client components (localStorage) and server contexts (passed via cookies).
 */
import type { AuthTokens, User } from '@/types';

const ACCESS_KEY = 'bm_access';
const REFRESH_KEY = 'bm_refresh';

export function storeTokens(tokens: AuthTokens): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ACCESS_KEY, tokens.access);
  localStorage.setItem(REFRESH_KEY, tokens.refresh);
}

export function getStoredTokens(): AuthTokens | null {
  if (typeof window === 'undefined') return null;
  const access = localStorage.getItem(ACCESS_KEY);
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!access || !refresh) return null;
  return { access, refresh };
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export async function signInWithGoogle(
  idToken: string
): Promise<{ tokens: AuthTokens; user: User }> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_token: idToken }),
  });
  if (!res.ok) throw new Error('Google sign-in failed');
  const data = await res.json();
  const tokens: AuthTokens = { access: data.access, refresh: data.refresh };
  storeTokens(tokens);
  return { tokens, user: data.user };
}

export async function refreshAccessToken(refreshToken: string): Promise<AuthTokens> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: refreshToken }),
  });
  if (!res.ok) throw new Error('Token refresh failed');
  const data = await res.json();
  const tokens: AuthTokens = { access: data.access, refresh: data.refresh };
  storeTokens(tokens);
  return tokens;
}

export async function signOut(accessToken: string): Promise<void> {
  try {
    await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/logout`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${accessToken}` },
    });
  } finally {
    clearTokens();
  }
}
