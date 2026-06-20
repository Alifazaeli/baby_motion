"use client";
import { useEffect, useRef, useState } from "react";
import { Play, Pause, SkipBack, SkipForward } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import type { StoryDraftDetail } from "@/lib/types";

interface Props {
  draft: StoryDraftDetail;
  language: string;
}

export function PreviewPlayer({ draft, language }: Props) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const segments = draft.segments;
  const seg = segments[currentIndex];
  const imageAsset = seg?.assets.find((a) => a.asset_type === "image");
  const audioAsset = seg?.assets.find((a) => a.asset_type === "audio" && a.language === language);
  const textAsset  = seg?.assets.find((a) => a.asset_type === "text"  && a.language === language);

  const hasAllAssets = segments.length > 0 && segments.every((s) => {
    const img = s.assets.find((a) => a.asset_type === "image");
    const aud = s.assets.find((a) => a.asset_type === "audio" && a.language === language);
    return img?.status === "ready" && aud?.status === "ready";
  });

  useEffect(() => {
    if (!playing || !audioAsset?.asset_url) return;
    const audio = new Audio(audioAsset.asset_url);
    audioRef.current = audio;
    audio.play().catch(() => {});
    audio.onended = () => {
      if (currentIndex < segments.length - 1) {
        setCurrentIndex((i) => i + 1);
      } else {
        setPlaying(false);
        setCurrentIndex(0);
      }
    };
    return () => { audio.pause(); audio.onended = null; };
  }, [playing, currentIndex, language]);

  return (
    <Card className="overflow-hidden bg-zinc-950 border-zinc-800 text-white">
      {/* Scene image */}
      <div className="aspect-[4/3] bg-zinc-900 relative">
        {imageAsset?.asset_url ? (
          <img src={imageAsset.asset_url} alt="" className="w-full h-full object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-zinc-600 text-sm">No image</div>
        )}
        <div className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded font-mono">
          {currentIndex + 1} / {segments.length}
        </div>
      </div>

      {/* Narration */}
      {textAsset?.content && (
        <div className="px-4 py-3 text-sm text-center leading-relaxed text-zinc-200" dir={language === "fa" ? "rtl" : "ltr"}>
          {textAsset.content}
        </div>
      )}

      <CardContent className="p-3">
        {/* Controls */}
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-zinc-400 hover:text-white hover:bg-zinc-800"
            disabled={currentIndex === 0}
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
          >
            <SkipBack className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            className="h-9 w-9 bg-white text-zinc-900 hover:bg-zinc-200"
            disabled={!hasAllAssets}
            onClick={() => setPlaying((p) => !p)}
          >
            {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 text-zinc-400 hover:text-white hover:bg-zinc-800"
            disabled={currentIndex === segments.length - 1}
            onClick={() => setCurrentIndex((i) => Math.min(segments.length - 1, i + 1))}
          >
            <SkipForward className="h-4 w-4" />
          </Button>
        </div>
        {!hasAllAssets && (
          <p className="text-center text-xs text-zinc-600 mt-2">Generate all assets to enable playback</p>
        )}
      </CardContent>
    </Card>
  );
}
