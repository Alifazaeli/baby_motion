"use client";
import useSWR from "swr";
import { categories as categoriesApi, languages as languagesApi } from "@/lib/api";
import { StoryWizard } from "@/components/StoryWizard";
import { Skeleton } from "@/components/ui/skeleton";

export default function NewStoryPage() {
  const { data: catsData, isLoading: catsLoading } = useSWR("categories", () => categoriesApi.list());
  const { data: langsData, isLoading: langsLoading } = useSWR("languages", () => languagesApi.list());

  const loading = catsLoading || langsLoading;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">New Story</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Describe your idea and Claude will break it into scenes
        </p>
      </div>
      {loading ? (
        <div className="max-w-2xl mx-auto space-y-4">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      ) : (
        <StoryWizard
          categories={catsData?.results ?? []}
          languages={langsData?.results ?? []}
        />
      )}
    </div>
  );
}
