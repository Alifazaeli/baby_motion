import { categories, languages } from "@/lib/api";
import { StoryWizard } from "@/components/StoryWizard";

export default async function NewStoryPage() {
  const [catsData, langsData] = await Promise.all([
    categories.list().catch(() => ({ results: [] })),
    languages.list().catch(() => ({ results: [] })),
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">New Story</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Describe your idea and Claude will break it into scenes
        </p>
      </div>
      <StoryWizard categories={catsData.results} languages={langsData.results} />
    </div>
  );
}
