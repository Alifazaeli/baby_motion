import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";
import type { AssetStatus, DraftStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const DRAFT_VARIANT: Record<DraftStatus, "default" | "secondary" | "destructive" | "outline"> = {
  drafting:   "secondary",
  generating: "outline",
  review:     "outline",
  published:  "default",
  archived:   "destructive",
};

const DRAFT_CLASS: Record<DraftStatus, string> = {
  drafting:   "text-muted-foreground",
  generating: "border-yellow-400 text-yellow-600",
  review:     "border-blue-400 text-blue-600",
  published:  "bg-green-600 hover:bg-green-600",
  archived:   "",
};

export function DraftStatusBadge({ status }: { status: DraftStatus }) {
  return (
    <Badge variant={DRAFT_VARIANT[status]} className={cn("gap-1 capitalize", DRAFT_CLASS[status])}>
      {status === "generating" && <Loader2 className="h-3 w-3 animate-spin" />}
      {status}
    </Badge>
  );
}

const ASSET_CLASS: Record<AssetStatus, string> = {
  pending:    "border-muted-foreground/30 text-muted-foreground",
  generating: "border-yellow-400 text-yellow-600",
  ready:      "border-green-500 text-green-700",
  stale:      "border-orange-400 text-orange-600",
  failed:     "border-destructive text-destructive",
};

export function AssetStatusBadge({ status }: { status: AssetStatus }) {
  return (
    <Badge variant="outline" className={cn("gap-1 capitalize text-xs", ASSET_CLASS[status])}>
      {status === "generating" && <Loader2 className="h-3 w-3 animate-spin" />}
      {status}
    </Badge>
  );
}
