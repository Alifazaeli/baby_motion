import { apiRequest } from './client';
import type {
  Category,
  Child,
  CreateChildInput,
  GetStoriesParams,
  MeResponse,
  Story,
  UpdateChildInput,
  ViewingSession,
} from '@/types';

export const api = {
  users: {
    getMe: () => apiRequest<MeResponse>('/me'),

    createChild: (data: CreateChildInput) =>
      apiRequest<{ child: Child }>('/children', {
        method: 'POST',
        body: JSON.stringify({
          name: data.name,
          birth_year: data.birthYear,
          birth_month: data.birthMonth,
          language: data.language,
        }),
      }),

    updateChild: (id: string, data: UpdateChildInput) =>
      apiRequest<{ child: Child }>(`/children/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          ...(data.name && { name: data.name }),
          ...(data.birthYear && { birth_year: data.birthYear }),
          ...(data.birthMonth && { birth_month: data.birthMonth }),
          ...(data.language && { language: data.language }),
        }),
      }),

    acknowledgeAgeGroup: (childId: string) =>
      apiRequest<void>(`/children/${childId}/acknowledge-age-group`, { method: 'POST' }),
  },

  content: {
    getCategories: (language: string) =>
      apiRequest<Category[]>('/categories', { language }),

    getStories: (params: GetStoriesParams) => {
      const qs = new URLSearchParams({
        child_id: params.childId,
        ...(params.language && { language: params.language }),
        ...(params.includeYounger && { include_younger: 'true' }),
        ...(params.category && { category: params.category }),
      });
      return apiRequest<Story[]>(`/stories?${qs}`, { language: params.language });
    },

    getStory: (id: string, language: string) =>
      apiRequest<Story>(`/stories/${id}`, { language }),
  },

  analytics: {
    startStory: (storyId: string, childId: string, language: string) =>
      apiRequest<ViewingSession>(`/stories/${storyId}/start`, {
        method: 'POST',
        body: JSON.stringify({ child_id: childId, language }),
      }),

    completeSession: (sessionId: string, scenesWatched: number) =>
      apiRequest<void>(`/sessions/${sessionId}/complete`, {
        method: 'POST',
        body: JSON.stringify({ scenes_watched: scenesWatched }),
      }),

    abandonSession: (sessionId: string, scenesWatched: number) =>
      apiRequest<void>(`/sessions/${sessionId}/abandon`, {
        method: 'POST',
        body: JSON.stringify({ scenes_watched: scenesWatched }),
      }),
  },

  i18n: {
    getStrings: (language: string) =>
      apiRequest<Record<string, string>>(`/i18n/${language}`),
  },
};
