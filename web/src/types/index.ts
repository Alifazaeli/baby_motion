export type AgeGroup = '12_18m' | '18_30m' | '30_42m' | '42_60m' | '60m_plus';
export type StoryStatus = 'draft' | 'review' | 'published' | 'archived';
export type Locale = 'fa' | 'en';

export interface User {
  id: string;
  googleSub: string;
  email?: string;
  displayName?: string;
  preferredLanguage: string;
  plan: 'free';
}

export interface Child {
  id: string;
  name: string;
  birthYear: number;
  birthMonth: number;
  language: string;
  ageInMonths: number;
  ageGroup: AgeGroup | null;
  nextAgeGroup: AgeGroup | null;
  daysToNextAgeGroup: number | null;
  hasPendingAgeGroupTransition: boolean;
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  iconUrl?: string;
  displayOrder: number;
}

export interface Story {
  id: string;
  slug: string;
  categoryId: string;
  ageGroup: AgeGroup;
  durationSeconds: number;
  coverUrl: string;
  status: StoryStatus;
  publishedAt?: string;
  title: string;
  description?: string;
  manifestUrl: string;
}

export interface Scene {
  index: number;
  imageUrl: string;
  text: string;
  audioStartSec: number;
  audioEndSec: number;
}

export interface Manifest {
  storyId: string;
  slug: string;
  language: string;
  title: string;
  durationSeconds: number;
  audioUrl: string;
  scenes: Scene[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface MeResponse {
  user: User;
  children: Child[];
}

export interface CreateChildInput {
  name: string;
  birthYear: number;
  birthMonth: number;
  language: string;
}

export interface UpdateChildInput {
  name?: string;
  birthYear?: number;
  birthMonth?: number;
  language?: string;
}

export interface GetStoriesParams {
  childId: string;
  language?: string;
  includeYounger?: boolean;
  category?: string;
}

export interface ViewingSession {
  sessionId: string;
}
