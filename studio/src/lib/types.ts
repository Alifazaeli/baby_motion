export type DraftStatus = "drafting" | "generating" | "review" | "published" | "archived";
export type AssetType = "text" | "image" | "audio";
export type AssetStatus = "pending" | "generating" | "ready" | "stale" | "failed";
export type JobStatus = "queued" | "running" | "completed" | "failed";
export type AgeGroup = "12_18m" | "18_30m" | "30_42m" | "42_60m";

export interface SegmentAsset {
  id: string;
  asset_type: AssetType;
  language: string | null;
  status: AssetStatus;
  content: string;
  asset_url: string;
  audio_start_sec: number | null;
  audio_end_sec: number | null;
  generation_cost_usd: string;
  generated_at: string | null;
  error_message: string;
  updated_at: string;
}

export interface StorySegment {
  id: string;
  index: number;
  image_prompt: string;
  status: AssetStatus;
  assets: SegmentAsset[];
  updated_at: string;
}

export interface StoryDraftSummary {
  id: string;
  title: string;
  age_groups: AgeGroup[];
  category_slug: string;
  languages: string[];
  status: DraftStatus;
  total_cost_usd: number;
  segment_count: number;
  created_at: string;
  updated_at: string;
}

export interface StoryDraftDetail extends Omit<StoryDraftSummary, "category_slug"> {
  idea_text: string;
  category: string;
  category_slug: string;
  style_block: string;
  linked_story: string | null;
  segments: StorySegment[];
}

export interface GenerationJob {
  id: string;
  job_type: "segmentation" | "image" | "audio";
  status: JobStatus;
  external_provider: string;
  segment: string | null;
  asset: string | null;
  started_at: string | null;
  finished_at: string | null;
  error_message: string;
  created_at: string;
}

export interface CategoryTranslation {
  language: string;
  name: string;
}

export interface Category {
  id: string;
  slug: string;
  icon_url: string;
  display_order: number;
  translations: CategoryTranslation[];
}

export interface Language {
  code: string;
  display_name: string;
  is_rtl: boolean;
  is_active: boolean;
}

export interface UIString {
  id: string;
  key: string;
  language: string;
  value: string;
}

export const AGE_GROUP_LABELS: Record<AgeGroup, string> = {
  "12_18m": "12–18 months",
  "18_30m": "18–30 months",
  "30_42m": "30–42 months",
  "42_60m": "42–60 months",
};

export const STATUS_COLORS: Record<DraftStatus, string> = {
  drafting: "bg-gray-100 text-gray-700",
  generating: "bg-yellow-100 text-yellow-700",
  review: "bg-blue-100 text-blue-700",
  published: "bg-green-100 text-green-700",
  archived: "bg-red-100 text-red-700",
};

export const ASSET_STATUS_COLORS: Record<AssetStatus, string> = {
  pending: "bg-gray-100 text-gray-600",
  generating: "bg-yellow-100 text-yellow-600 animate-pulse",
  ready: "bg-green-100 text-green-700",
  stale: "bg-orange-100 text-orange-700",
  failed: "bg-red-100 text-red-700",
};
