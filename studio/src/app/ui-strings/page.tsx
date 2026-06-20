"use client";
import { useState } from "react";
import useSWR from "swr";
import { Pencil, Check, X, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { uiStrings } from "@/lib/api";
import type { UIString } from "@/lib/types";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";

export default function UIStringsPage() {
  const [langFilter, setLangFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [saving, setSaving] = useState(false);

  const params: Record<string, string> = {};
  if (langFilter !== "all") params.language = langFilter;
  if (query) params.q = query;

  const { data, isLoading, mutate } = useSWR(
    ["ui-strings", langFilter, query],
    () => uiStrings.list(Object.keys(params).length ? params : undefined)
  );

  async function save(id: string) {
    setSaving(true);
    try {
      await uiStrings.update(id, editValue);
      await mutate();
      setEditing(null);
      toast.success("String updated");
    } catch {
      toast.error("Failed to update string");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">UI Strings</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Manage translated UI strings served to client apps
        </p>
      </div>

      {/* Filters */}
      <div className="flex gap-3 flex-wrap">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by key…"
          className="w-56 h-8 text-sm"
        />
        <Select value={langFilter} onValueChange={setLangFilter}>
          <SelectTrigger className="w-40 h-8 text-sm">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All languages</SelectItem>
            <SelectItem value="fa">Persian (fa)</SelectItem>
            <SelectItem value="en">English (en)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-80">Key</TableHead>
                <TableHead className="w-20">Lang</TableHead>
                <TableHead>Value</TableHead>
                <TableHead className="w-20" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && Array.from({ length: 8 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 4 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                  ))}
                </TableRow>
              ))}
              {data?.results.map((s: UIString) => (
                <TableRow key={s.id}>
                  <TableCell className="font-mono text-xs text-muted-foreground">{s.key}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">{s.language.toUpperCase()}</Badge>
                  </TableCell>
                  <TableCell>
                    {editing === s.id ? (
                      <Input
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="h-8 text-sm"
                        dir={s.language === "fa" ? "rtl" : "ltr"}
                        autoFocus
                      />
                    ) : (
                      <span
                        dir={s.language === "fa" ? "rtl" : "ltr"}
                        className="text-sm"
                      >
                        {s.value || (
                          <span className="inline-flex items-center gap-1 text-destructive text-xs">
                            <AlertCircle className="h-3 w-3" /> missing
                          </span>
                        )}
                      </span>
                    )}
                  </TableCell>
                  <TableCell>
                    {editing === s.id ? (
                      <div className="flex gap-1 justify-end">
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => save(s.id)} disabled={saving}>
                          <Check className="h-3.5 w-3.5 text-green-600" />
                        </Button>
                        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => setEditing(null)}>
                          <X className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex justify-end">
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7"
                          onClick={() => { setEditing(s.id); setEditValue(s.value); }}
                        >
                          <Pencil className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
