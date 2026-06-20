"use client";
import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { Plus, Trash2, X, Check } from "lucide-react";
import { languages } from "@/lib/api";
import type { Language } from "@/lib/types";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const BLANK = { code: "", display_name: "", is_rtl: false, is_active: true };

export default function LanguagesPage() {
  const { data, isLoading, mutate } = useSWR("languages", () => languages.list());
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ ...BLANK });
  const [saving, setSaving] = useState(false);

  async function toggleActive(lang: Language) {
    try {
      await languages.update(lang.code, { is_active: !lang.is_active });
      await mutate();
      toast.success(`${lang.display_name} ${!lang.is_active ? "enabled" : "disabled"}`);
    } catch {
      toast.error("Failed to update language");
    }
  }

  async function saveCreate() {
    if (!form.code.trim() || !form.display_name.trim()) {
      toast.error("Code and display name are required");
      return;
    }
    setSaving(true);
    try {
      await languages.create({
        code: form.code.trim().toLowerCase(),
        display_name: form.display_name.trim(),
        is_rtl: form.is_rtl,
        is_active: form.is_active,
      });
      await mutate();
      setCreating(false);
      setForm({ ...BLANK });
      toast.success("Language added");
    } catch {
      toast.error("Failed to add language");
    } finally {
      setSaving(false);
    }
  }

  async function deleteLang(lang: Language) {
    if (!confirm(`Delete "${lang.display_name}"? This cannot be undone.`)) return;
    try {
      await languages.delete(lang.code);
      await mutate();
      toast.success(`${lang.display_name} deleted`);
    } catch {
      toast.error("Failed to delete language — it may be in use");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Languages</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Active languages are available for story generation and client apps.
          </p>
        </div>
        {!creating && (
          <Button size="sm" onClick={() => { setCreating(true); setForm({ ...BLANK }); }}>
            <Plus className="h-4 w-4 mr-1.5" />New language
          </Button>
        )}
      </div>

      {/* Create form */}
      {creating && (
        <Card className="border-primary/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">New language</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">Code (BCP-47) *</p>
                <Input
                  value={form.code}
                  onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))}
                  placeholder="fa"
                  className="h-8 text-sm font-mono w-24"
                  maxLength={10}
                />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">Display name *</p>
                <Input
                  value={form.display_name}
                  onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))}
                  placeholder="Persian"
                  className="h-8 text-sm"
                />
              </div>
            </div>
            <div className="flex gap-6">
              <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
                <Switch
                  checked={form.is_rtl}
                  onCheckedChange={(v) => setForm((f) => ({ ...f, is_rtl: v }))}
                />
                Right-to-left (RTL)
              </label>
              <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
                <Switch
                  checked={form.is_active}
                  onCheckedChange={(v) => setForm((f) => ({ ...f, is_active: v }))}
                />
                Active
              </label>
            </div>
            <div className="flex gap-2 pt-1">
              <Button size="sm" onClick={saveCreate} disabled={saving}>
                <Check className="h-3.5 w-3.5 mr-1.5" />Save
              </Button>
              <Button size="sm" variant="outline" onClick={() => setCreating(false)}>
                <X className="h-3.5 w-3.5 mr-1.5" />Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">Code</TableHead>
                <TableHead>Display name</TableHead>
                <TableHead className="w-24">Direction</TableHead>
                <TableHead className="w-20">Active</TableHead>
                <TableHead className="w-12" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && Array.from({ length: 2 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 5 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                  ))}
                </TableRow>
              ))}
              {data?.results.map((lang: Language) => (
                <TableRow key={lang.code}>
                  <TableCell>
                    <Badge variant="outline" className="font-mono font-semibold">{lang.code}</Badge>
                  </TableCell>
                  <TableCell className="font-medium">{lang.display_name}</TableCell>
                  <TableCell>
                    <span className="text-sm text-muted-foreground">
                      {lang.is_rtl ? "RTL" : "LTR"}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Switch
                      checked={lang.is_active}
                      onCheckedChange={() => toggleActive(lang)}
                    />
                  </TableCell>
                  <TableCell>
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7 text-destructive hover:text-destructive"
                      onClick={() => deleteLang(lang)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
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
