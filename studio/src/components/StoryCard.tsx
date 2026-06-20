import Link from "next/link";
import { Clock, Layers } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DraftStatusBadge } from "./GenerationStatusBadge";
import { AGE_GROUP_LABELS } from "@/lib/types";
import type { StoryDraftSummary } from "@/lib/types";

export function StoryCard({ draft }: { draft: StoryDraftSummary }) {
  return (
    <Link href={`/stories/${draft.id}`}>
      <Card className="h-full cursor-pointer transition-shadow hover:shadow-md hover:border-primary/30">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-sm leading-snug line-clamp-2 flex-1">
              {draft.title || <span className="text-muted-foreground italic">Untitled</span>}
            </h3>
            <DraftStatusBadge status={draft.status} />
          </div>
        </CardHeader>
        <CardContent className="pb-4 space-y-3">
          <div className="flex flex-wrap gap-1.5">
            <Badge variant="secondary" className="text-xs">{AGE_GROUP_LABELS[draft.age_group]}</Badge>
            <Badge variant="outline" className="text-xs">{draft.category_slug}</Badge>
            {draft.languages.map((l) => (
              <Badge key={l} variant="outline" className="text-xs text-primary border-primary/40">{l.toUpperCase()}</Badge>
            ))}
          </div>

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <Layers className="h-3 w-3" />
              {draft.segment_count} scene{draft.segment_count !== 1 ? "s" : ""}
            </span>
            <span className="font-mono">${Number(draft.total_cost_usd).toFixed(4)}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
