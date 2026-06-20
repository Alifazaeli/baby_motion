"use client";
import { useState } from "react";
import { RefreshCw, ImageIcon, AudioLines, Pencil, Check, X } from "lucide-react";
import { assets, segments } from "@/lib/api";
import { AssetStatusBadge } from "./GenerationStatusBadge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { SegmentAsset, StoryDraftDetail, StorySegment } from "@/lib/types";

interface Props {
  segment: StorySegment;
  draft: StoryDraftDetail;
  onRefresh: () => void;
}

export function SegmentEditor({ segment, draft, onRefresh }: Props) {
  const [editingPrompt, setEditingPrompt] = useState(false);
  const [prompt, setPrompt] = useState(segment.image_prompt);
  const [saving, setSaving] = useState(false);

  const imageAsset = segment.assets.find((a) => a.asset_type === "image");
  const textAssets = segment.assets.filter((a) => a.asset_type === "text");
  const audioAssets = segment.assets.filter((a) => a.asset_type === "audio");

  async function savePrompt() {
    setSaving(true);
    try {
      await segments.update(segment.id, { image_prompt: prompt });
      setEditingPrompt(false);
      onRefresh();
    } finally {
      setSaving(false);
    }
  }

  async function regenImage() {
    await segments.generateImage(segment.id);
    onRefresh();
  }

  async function regenAsset(assetId: string) {
    await assets.regenerate(assetId);
    onRefresh();
  }

  async function regenAudio(lang: string) {
    await segments.generateAudio(segment.id, lang);
    onRefresh();
  }

  async function saveNarration(assetId: string, content: string) {
    await assets.update(assetId, { content });
    onRefresh();
  }

  return (
    <Card>
      <CardHeader className="pb-3 flex-row items-center justify-between space-y-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-muted-foreground">Scene {segment.index + 1}</span>
          <AssetStatusBadge status={segment.status} />
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs defaultValue="image">
          <TabsList className="w-full rounded-none border-b bg-transparent h-9">
            <TabsTrigger value="image" className="flex items-center gap-1.5 text-xs">
              <ImageIcon className="h-3.5 w-3.5" /> Image
            </TabsTrigger>
            <TabsTrigger value="narration" className="flex items-center gap-1.5 text-xs">
              <Pencil className="h-3.5 w-3.5" /> Narration
            </TabsTrigger>
            <TabsTrigger value="audio" className="flex items-center gap-1.5 text-xs">
              <AudioLines className="h-3.5 w-3.5" /> Audio
            </TabsTrigger>
          </TabsList>

          {/* Image tab */}
          <TabsContent value="image" className="p-4 space-y-3">
            {imageAsset?.asset_url ? (
              <img
                src={imageAsset.asset_url}
                alt={`Scene ${segment.index}`}
                className="w-full aspect-[4/3] object-cover rounded-lg border"
              />
            ) : (
              <div className="w-full aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
                <p className="text-muted-foreground text-sm">No image generated yet</p>
              </div>
            )}

            {imageAsset && (
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <AssetStatusBadge status={imageAsset.status} />
                <span className="font-mono">${Number(imageAsset.generation_cost_usd).toFixed(4)}</span>
              </div>
            )}

            <Separator />

            {/* Image prompt editor */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Prompt</span>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2 text-xs"
                  onClick={() => { setEditingPrompt(!editingPrompt); setPrompt(segment.image_prompt); }}
                >
                  {editingPrompt ? <X className="h-3 w-3" /> : <Pencil className="h-3 w-3" />}
                </Button>
              </div>
              {editingPrompt ? (
                <div className="space-y-2">
                  <Textarea rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} className="text-xs" />
                  <div className="flex gap-2">
                    <Button size="sm" className="h-7 text-xs" onClick={savePrompt} disabled={saving}>
                      <Check className="h-3 w-3 mr-1" /> Save
                    </Button>
                    <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => setEditingPrompt(false)}>Cancel</Button>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground leading-relaxed">{prompt || "—"}</p>
              )}
            </div>

            <Button variant="outline" size="sm" className="w-full gap-2" onClick={regenImage}>
              <RefreshCw className="h-3.5 w-3.5" /> Regenerate image
            </Button>
          </TabsContent>

          {/* Narration tab */}
          <TabsContent value="narration" className="p-4 space-y-4">
            {draft.languages.map((lang) => {
              const ta = textAssets.find((a) => a.language === lang);
              return (
                <NarrationField
                  key={lang}
                  lang={lang}
                  asset={ta ?? null}
                  onSave={(content) => ta ? saveNarration(ta.id, content) : Promise.resolve()}
                />
              );
            })}
          </TabsContent>

          {/* Audio tab */}
          <TabsContent value="audio" className="p-4 space-y-4">
            {draft.languages.map((lang) => {
              const aa = audioAssets.find((a) => a.language === lang);
              return (
                <div key={lang} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wide">{lang}</span>
                    <div className="flex items-center gap-2">
                      {aa && <AssetStatusBadge status={aa.status} />}
                      {aa?.audio_end_sec && (
                        <span className="text-xs text-muted-foreground font-mono">
                          {aa.audio_end_sec.toFixed(1)}s
                        </span>
                      )}
                    </div>
                  </div>
                  {aa?.status === "stale" && (
                    <p className="text-xs text-orange-600 bg-orange-50 rounded px-2 py-1">
                      Narration changed — audio is stale
                    </p>
                  )}
                  {aa?.asset_url && aa.status === "ready" && (
                    <audio controls src={aa.asset_url} className="w-full h-8" />
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full gap-2"
                    onClick={() => aa ? regenAsset(aa.id) : regenAudio(lang)}
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    {aa ? "Regenerate" : "Generate"} audio
                  </Button>
                  {aa && (
                    <p className="text-xs text-muted-foreground text-right font-mono">
                      ${Number(aa.generation_cost_usd).toFixed(4)}
                    </p>
                  )}
                </div>
              );
            })}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function NarrationField({
  lang,
  asset,
  onSave,
}: {
  lang: string;
  asset: SegmentAsset | null;
  onSave: (content: string) => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(asset?.content ?? "");
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await onSave(value);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide">{lang}</span>
          {asset && <AssetStatusBadge status={asset.status} />}
        </div>
        {asset && (
          <Button
            variant="ghost"
            size="sm"
            className="h-6 px-2 text-xs"
            onClick={() => { setValue(asset.content); setEditing(!editing); }}
          >
            {editing ? <X className="h-3 w-3" /> : <Pencil className="h-3 w-3" />}
          </Button>
        )}
      </div>

      {editing ? (
        <div className="space-y-2">
          <Textarea
            value={value}
            onChange={(e) => setValue(e.target.value)}
            rows={3}
            className="text-sm"
            dir={lang === "fa" ? "rtl" : "ltr"}
          />
          <div className="flex gap-2">
            <Button size="sm" className="h-7 text-xs" onClick={save} disabled={saving}>
              <Check className="h-3 w-3 mr-1" /> Save
            </Button>
            <Button size="sm" variant="ghost" className="h-7 text-xs" onClick={() => setEditing(false)}>Cancel</Button>
          </div>
        </div>
      ) : (
        <p
          className="text-sm text-muted-foreground leading-relaxed min-h-[2rem]"
          dir={lang === "fa" ? "rtl" : "ltr"}
        >
          {asset?.content || <span className="italic text-xs">No text yet</span>}
        </p>
      )}
    </div>
  );
}
