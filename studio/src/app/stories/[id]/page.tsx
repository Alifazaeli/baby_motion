"use client";
import { useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import useSWR from "swr";
import {
  ChevronLeft,
  Loader2,
  Wand2,
  Zap,
  Eye,
  EyeOff,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";
import { drafts } from "@/lib/api";
import { SegmentEditor } from "@/components/SegmentEditor";
import { DraftStatusBadge } from "@/components/GenerationStatusBadge";
import { PreviewPlayer } from "@/components/PreviewPlayer";
import { useJobStatus } from "@/hooks/useJobStatus";
import { AGE_GROUP_LABELS } from "@/lib/types";
import type { StoryDraftDetail } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function StoryDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [previewLang, setPreviewLang] = useState("fa");
  const [showPreview, setShowPreview] = useState(false);
  const [publishing, setPublishing] = useState(false);

  const { data: draft, error, mutate } = useSWR<StoryDraftDetail>(
    `draft-${id}`,
    () => drafts.get(id)
  );

  const { jobs, hasActive } = useJobStatus(id);

  useSWR(
    hasActive ? `draft-${id}-poll` : null,
    () => drafts.get(id),
    { refreshInterval: 3000, onSuccess: (d) => mutate(d, false) }
  );

  const onRefresh = useCallback(() => mutate(), [mutate]);

  async function runSegmentation() {
    try {
      await drafts.segment(id);
      toast.success("Segmentation started");
      onRefresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to start segmentation");
    }
  }

  async function generateAll() {
    try {
      const result = await drafts.generateAssets(id);
      toast.success(`Queued ${result.jobs_queued} generation job(s)`);
      onRefresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Failed to queue generation");
    }
  }

  async function publish() {
    setPublishing(true);
    try {
      await drafts.publish(id);
      toast.success("Story published successfully");
      onRefresh();
    } catch (e: unknown) {
      toast.error(e instanceof Error ? e.message : "Publish failed");
    } finally {
      setPublishing(false);
    }
  }

  if (error) return (
    <Alert variant="destructive" className="max-w-lg">
      <AlertCircle className="h-4 w-4" />
      <AlertDescription>Failed to load story draft.</AlertDescription>
    </Alert>
  );

  if (!draft) return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-96" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-6">
        {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-64 rounded-xl" />)}
      </div>
    </div>
  );

  const allReady = draft.segments.length > 0 && draft.segments.every((s) => s.status === "ready");
  const hasSegments = draft.segments.length > 0;
  const runningCount = jobs.filter((j) => j.status === "running").length;
  const queuedCount = jobs.filter((j) => j.status === "queued").length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Button variant="ghost" size="sm" className="mb-3 -ml-2 text-muted-foreground" onClick={() => router.push("/stories")}>
          <ChevronLeft className="h-4 w-4 mr-1" /> Stories
        </Button>

        <div className="flex items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl font-bold tracking-tight">
                {draft.title || <span className="text-muted-foreground italic font-normal">Untitled</span>}
              </h1>
              <DraftStatusBadge status={draft.status} />
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground flex-wrap">
              <span>{draft.age_groups.map((ag) => AGE_GROUP_LABELS[ag]).join(" · ")}</span>
              <span>·</span>
              <span>{draft.languages.join(", ").toUpperCase()}</span>
              <span>·</span>
              <span className="font-mono">${Number(draft.total_cost_usd).toFixed(4)} total</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 shrink-0">
            {!hasSegments && (
              <Button onClick={runSegmentation} disabled={hasActive} size="sm">
                {hasActive ? <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" /> : <Wand2 className="h-3.5 w-3.5 mr-2" />}
                Run segmentation
              </Button>
            )}
            {hasSegments && draft.status !== "published" && (
              <Button variant="outline" size="sm" onClick={generateAll} disabled={hasActive}>
                {hasActive ? <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" /> : <Zap className="h-3.5 w-3.5 mr-2" />}
                Generate all assets
              </Button>
            )}
            {hasSegments && (
              <Button variant="outline" size="sm" onClick={() => setShowPreview(!showPreview)}>
                {showPreview ? <EyeOff className="h-3.5 w-3.5 mr-2" /> : <Eye className="h-3.5 w-3.5 mr-2" />}
                {showPreview ? "Hide" : "Preview"}
              </Button>
            )}
            {draft.status === "review" && allReady && (
              <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={publish} disabled={publishing}>
                {publishing ? <Loader2 className="h-3.5 w-3.5 mr-2 animate-spin" /> : <CheckCircle className="h-3.5 w-3.5 mr-2" />}
                Publish
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Generation progress banner */}
      {hasActive && (
        <Alert className="border-yellow-200 bg-yellow-50 text-yellow-800">
          <Loader2 className="h-4 w-4 animate-spin" />
          <AlertDescription>
            Generation in progress — {runningCount} running, {queuedCount} queued
          </AlertDescription>
        </Alert>
      )}

      {/* Story idea */}
      <Card className="bg-muted/30">
        <CardContent className="py-3 px-4">
          <p className="text-sm">
            <span className="font-medium text-muted-foreground mr-2">Idea:</span>
            {draft.idea_text}
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Segments — 2/3 width */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-semibold">
              Scenes <span className="text-muted-foreground font-normal">({draft.segments.length})</span>
            </h2>
          </div>

          {draft.segments.length === 0 ? (
            <Card className="border-dashed">
              <CardContent className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <div className="text-4xl mb-3">🎬</div>
                <p className="font-medium">No scenes yet</p>
                <p className="text-sm mt-1">Run segmentation to generate scenes from your idea</p>
              </CardContent>
            </Card>
          ) : (
            draft.segments.map((seg) => (
              <SegmentEditor key={seg.id} segment={seg} draft={draft} onRefresh={onRefresh} />
            ))
          )}
        </div>

        {/* Sidebar — 1/3 width */}
        <div className="space-y-4">
          {/* Preview */}
          {showPreview && hasSegments && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Preview</h3>
                <Select value={previewLang} onValueChange={setPreviewLang}>
                  <SelectTrigger className="w-20 h-7 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {draft.languages.map((l) => (
                      <SelectItem key={l} value={l}>{l.toUpperCase()}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <PreviewPlayer draft={draft} language={previewLang} />
            </div>
          )}

          {/* Style block */}
          {draft.style_block && (
            <Card>
              <CardHeader className="pb-2 pt-4 px-4">
                <CardTitle className="text-sm">Style block</CardTitle>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <p className="text-xs text-muted-foreground leading-relaxed">{draft.style_block}</p>
              </CardContent>
            </Card>
          )}

          {/* Recent jobs */}
          {jobs.length > 0 && (
            <Card>
              <CardHeader className="pb-2 pt-4 px-4">
                <CardTitle className="text-sm">Generation jobs</CardTitle>
              </CardHeader>
              <CardContent className="px-4 pb-4 space-y-1.5">
                {jobs.slice(0, 10).map((job) => (
                  <div key={job.id} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground capitalize">
                      {job.job_type} / {job.external_provider}
                    </span>
                    <Badge
                      variant="outline"
                      className={{
                        completed: "border-green-400 text-green-700",
                        failed: "border-destructive text-destructive",
                        running: "border-yellow-400 text-yellow-600",
                        queued: "text-muted-foreground",
                      }[job.status]}
                    >
                      {job.status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
