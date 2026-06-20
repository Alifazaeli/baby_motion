"use client";
import { useState } from "react";
import Link from "next/link";
import useSWR from "swr";
import { Plus, Search } from "lucide-react";
import { drafts } from "@/lib/api";
import { StoryCard } from "@/components/StoryCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AgeGroup, DraftStatus } from "@/lib/types";
import { AGE_GROUP_LABELS } from "@/lib/types";

const ALL_STATUSES: DraftStatus[] = ["drafting", "generating", "review", "published", "archived"];

export default function StoriesPage() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [ageFilter, setAgeFilter] = useState<string>("all");

  const params: Record<string, string> = {};
  if (statusFilter !== "all") params.status = statusFilter;
  if (ageFilter !== "all") params.age_group = ageFilter;

  const { data, isLoading } = useSWR(
    ["drafts", statusFilter, ageFilter],
    () => drafts.list(Object.keys(params).length ? params : undefined)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Stories</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            {data?.count ?? "–"} draft{data?.count !== 1 ? "s" : ""} total
          </p>
        </div>
        <Button asChild>
          <Link href="/stories/new">
            <Plus className="h-4 w-4 mr-2" /> New story
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-36 h-8 text-sm">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {ALL_STATUSES.map((s) => (
              <SelectItem key={s} value={s} className="capitalize">{s}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={ageFilter} onValueChange={setAgeFilter}>
          <SelectTrigger className="w-36 h-8 text-sm">
            <SelectValue placeholder="Age group" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All ages</SelectItem>
            {(Object.entries(AGE_GROUP_LABELS) as [AgeGroup, string][]).map(([k, label]) => (
              <SelectItem key={k} value={k}>{label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-xl" />
          ))}
        </div>
      ) : data?.results.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center text-muted-foreground">
          <div className="text-5xl mb-4">📖</div>
          <p className="font-medium">No stories yet</p>
          <p className="text-sm mt-1">
            <Link href="/stories/new" className="text-primary hover:underline">Create your first story →</Link>
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {data?.results.map((draft) => (
            <StoryCard key={draft.id} draft={draft} />
          ))}
        </div>
      )}
    </div>
  );
}
