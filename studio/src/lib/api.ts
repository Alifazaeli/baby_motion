/**
 * Typed API client for the Content Studio backend (/studio/api/).
 * All requests attach the stored JWT as a Bearer token.
 */

const API_BASE =
  typeof window !== "undefined"
    ? "/studio/api"  // proxy rewrite in next.config.ts
    : `${process.env.NEXT_PUBLIC_API_URL}/studio/api`;

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("studio_access_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────

export async function studioLogin(email: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? "Login failed");
  }
  const data = await res.json();
  localStorage.setItem("studio_access_token", data.access);
  localStorage.setItem("studio_refresh_token", data.refresh);
  return data;
}

export function logout() {
  localStorage.removeItem("studio_access_token");
  localStorage.removeItem("studio_refresh_token");
}

// ── Drafts ────────────────────────────────────────────────────────────────

import type {
  Category,
  GenerationJob,
  Language,
  SegmentAsset,
  StoryDraftDetail,
  StoryDraftSummary,
  StorySegment,
  UIString,
} from "./types";

export const drafts = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return request<{ results: StoryDraftSummary[]; count: number }>(`/drafts/${qs}`);
  },
  get: (id: string) => request<StoryDraftDetail>(`/drafts/${id}/`),
  create: (data: { title?: string; idea_text: string; age_group: string; category: string; languages: string[] }) =>
    request<StoryDraftDetail>(`/drafts/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<StoryDraftDetail>) =>
    request<StoryDraftDetail>(`/drafts/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/drafts/${id}/`, { method: "DELETE" }),
  segment: (id: string) =>
    request<{ job_id: string }>(`/drafts/${id}/segment/`, { method: "POST" }),
  generateAssets: (id: string, params?: { asset_type?: string; language?: string }) =>
    request<{ jobs_queued: number; job_ids: string[] }>(`/drafts/${id}/generate-assets/`, {
      method: "POST",
      body: JSON.stringify(params ?? {}),
    }),
  publish: (id: string) =>
    request<StoryDraftDetail>(`/drafts/${id}/publish/`, { method: "POST" }),
  jobs: (id: string) => request<GenerationJob[]>(`/drafts/${id}/jobs/`),
};

// ── Segments ──────────────────────────────────────────────────────────────

export const segments = {
  update: (id: string, data: { image_prompt?: string }) =>
    request<StorySegment>(`/segments/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  generateImage: (id: string) =>
    request<{ job_id: string }>(`/segments/${id}/generate-image/`, { method: "POST" }),
  generateAudio: (id: string, language: string) =>
    request<{ job_id: string }>(`/segments/${id}/generate-audio/`, {
      method: "POST",
      body: JSON.stringify({ language }),
    }),
};

// ── Assets ────────────────────────────────────────────────────────────────

export const assets = {
  update: (id: string, data: { content?: string }) =>
    request<SegmentAsset>(`/assets/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  regenerate: (id: string) =>
    request<{ job_id: string }>(`/assets/${id}/regenerate/`, { method: "POST" }),
};

// ── Categories ────────────────────────────────────────────────────────────

export const categories = {
  list: () => request<{ results: Category[] }>("/categories/"),
  create: (data: Partial<Category>) =>
    request<Category>("/categories/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Category>) =>
    request<Category>(`/categories/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/categories/${id}/`, { method: "DELETE" }),
};

// ── Languages ─────────────────────────────────────────────────────────────

export const languages = {
  list: () => request<{ results: Language[] }>("/languages/"),
  create: (data: Partial<Language>) =>
    request<Language>("/languages/", { method: "POST", body: JSON.stringify(data) }),
  update: (code: string, data: Partial<Language>) =>
    request<Language>(`/languages/${code}/`, { method: "PATCH", body: JSON.stringify(data) }),
};

// ── UI Strings ────────────────────────────────────────────────────────────

export const uiStrings = {
  list: (params?: { language?: string; q?: string }) => {
    const qs = params ? "?" + new URLSearchParams(params as Record<string, string>).toString() : "";
    return request<{ results: UIString[] }>(`/ui-strings/${qs}`);
  },
  update: (id: string, value: string) =>
    request<UIString>(`/ui-strings/${id}/`, { method: "PATCH", body: JSON.stringify({ value }) }),
};

// ── Analytics ─────────────────────────────────────────────────────────────

export const analytics = {
  get: () => request<{ top_stories: { story__slug: string; views: number }[] }>("/analytics/"),
};
