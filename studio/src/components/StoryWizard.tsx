"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Wand2 } from "lucide-react";
import { drafts, categories as categoriesApi, languages as languagesApi } from "@/lib/api";
import type { AgeGroup, Category, Language } from "@/lib/types";
import { AGE_GROUP_LABELS } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface Props {
  categories: Category[];
  languages: Language[];
}

export function StoryWizard({ categories, languages }: Props) {
  const router = useRouter();
  const [ideaText, setIdeaText] = useState("");
  const [ageGroup, setAgeGroup] = useState<AgeGroup>("30_42m");
  const [categoryId, setCategoryId] = useState(categories[0]?.id ?? "");
  const [selectedLangs, setSelectedLangs] = useState<string[]>(["fa", "en"]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function toggleLang(code: string) {
    setSelectedLangs((prev) =>
      prev.includes(code) ? prev.filter((l) => l !== code) : [...prev, code]
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!ideaText.trim()) { setError("Please enter a story idea."); return; }
    if (!selectedLangs.length) { setError("Select at least one language."); return; }
    setError("");
    setLoading(true);
    try {
      const draft = await drafts.create({
        title: title.trim() || undefined,
        idea_text: ideaText.trim(),
        age_group: ageGroup,
        category: categoryId,
        languages: selectedLangs,
      });
      await drafts.segment(draft.id);
      router.push(`/stories/${draft.id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to create draft.");
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
              <Wand2 className="h-4 w-4 text-primary" />
            </div>
            <div>
              <CardTitle>New Story</CardTitle>
              <CardDescription>
                Describe your idea — Claude will segment it into scenes with narration and image prompts
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-5">
            {/* Story idea */}
            <div className="space-y-2">
              <Label htmlFor="idea">
                Story idea <span className="text-destructive">*</span>
              </Label>
              <Textarea
                id="idea"
                placeholder="e.g. A sleepy little bear who can't find his favorite blanket before bedtime…"
                rows={4}
                value={ideaText}
                onChange={(e) => setIdeaText(e.target.value)}
                required
              />
            </div>

            {/* Working title */}
            <div className="space-y-2">
              <Label htmlFor="title">
                Working title <span className="text-muted-foreground text-xs">(optional)</span>
              </Label>
              <Input
                id="title"
                placeholder="The Sleepy Bear"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Age group */}
              <div className="space-y-2">
                <Label>Age group</Label>
                <Select value={ageGroup} onValueChange={(v) => setAgeGroup(v as AgeGroup)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {(Object.entries(AGE_GROUP_LABELS) as [AgeGroup, string][]).map(([k, label]) => (
                      <SelectItem key={k} value={k}>{label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label>Category</Label>
                <Select value={categoryId} onValueChange={setCategoryId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((c) => (
                      <SelectItem key={c.id} value={c.id}>{c.slug}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Languages */}
            <div className="space-y-2">
              <Label>Languages</Label>
              <div className="flex flex-wrap gap-2">
                {languages.filter((l) => l.is_active).map((l) => (
                  <button
                    key={l.code}
                    type="button"
                    onClick={() => toggleLang(l.code)}
                    className={cn(
                      "inline-flex items-center rounded-md border px-3 py-1.5 text-sm font-medium transition-colors",
                      selectedLangs.includes(l.code)
                        ? "border-primary bg-primary text-primary-foreground"
                        : "border-input bg-background hover:bg-accent hover:text-accent-foreground"
                    )}
                  >
                    {l.display_name}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button type="submit" className="w-full" size="lg" disabled={loading}>
              {loading
                ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating draft & running segmentation…</>
                : <><Wand2 className="mr-2 h-4 w-4" />Create story</>
              }
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
