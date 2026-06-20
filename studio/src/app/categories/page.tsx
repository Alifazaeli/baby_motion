"use client";
import { useState } from "react";
import useSWR from "swr";
import { Pencil, Trash2, Check, X, Plus } from "lucide-react";
import { toast } from "sonner";
import { categories } from "@/lib/api";
import type { Category, CategoryTranslation } from "@/lib/types";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

type TranslationDraft = { language: string; name: string };

const BLANK_CREATE = { slug: "", icon_url: "", display_order: 0, translations: [{ language: "fa", name: "" }, { language: "en", name: "" }] };

export default function CategoriesPage() {
  const { data, isLoading, mutate } = useSWR("categories", () => categories.list());
  const [editing, setEditing] = useState<string | null>(null);
  const [editForm, setEditForm] = useState({ slug: "", icon_url: "", display_order: 0, translations: [] as TranslationDraft[] });
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState({ ...BLANK_CREATE });
  const [saving, setSaving] = useState(false);

  function startEdit(cat: Category) {
    setCreating(false);
    setEditing(cat.id);
    setEditForm({
      slug: cat.slug,
      icon_url: cat.icon_url,
      display_order: cat.display_order,
      translations: cat.translations.map((t) => ({ language: t.language, name: t.name })),
    });
  }

  function setEditTranslation(lang: string, name: string) {
    setEditForm((f) => ({
      ...f,
      translations: f.translations.some((t) => t.language === lang)
        ? f.translations.map((t) => t.language === lang ? { ...t, name } : t)
        : [...f.translations, { language: lang, name }],
    }));
  }

  function setCreateTranslation(idx: number, field: keyof TranslationDraft, value: string) {
    setCreateForm((f) => {
      const ts = [...f.translations];
      ts[idx] = { ...ts[idx], [field]: value };
      return { ...f, translations: ts };
    });
  }

  async function saveEdit(id: string) {
    setSaving(true);
    try {
      await categories.update(id, editForm);
      await mutate();
      setEditing(null);
      toast.success("Category updated");
    } catch {
      toast.error("Failed to update category");
    } finally {
      setSaving(false);
    }
  }

  async function saveCreate() {
    if (!createForm.slug.trim()) { toast.error("Slug is required"); return; }
    setSaving(true);
    try {
      await categories.create({
        slug: createForm.slug.trim(),
        icon_url: createForm.icon_url.trim(),
        display_order: createForm.display_order,
        translations: createForm.translations.filter((t) => t.language && t.name),
      });
      await mutate();
      setCreating(false);
      setCreateForm({ ...BLANK_CREATE });
      toast.success("Category created");
    } catch {
      toast.error("Failed to create category");
    } finally {
      setSaving(false);
    }
  }

  async function deleteCategory(id: string) {
    if (!confirm("Delete this category? Stories linked to it will be affected.")) return;
    try {
      await categories.delete(id);
      await mutate();
      toast.success("Category deleted");
    } catch {
      toast.error("Failed to delete category");
    }
  }

  const langs = ["fa", "en"];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Categories</h1>
          <p className="text-sm text-muted-foreground mt-0.5">Manage story categories and their translations</p>
        </div>
        {!creating && (
          <Button size="sm" onClick={() => { setEditing(null); setCreating(true); setCreateForm({ ...BLANK_CREATE }); }}>
            <Plus className="h-4 w-4 mr-1.5" />New category
          </Button>
        )}
      </div>

      {/* Create form */}
      {creating && (
        <Card className="border-primary/40">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">New category</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">Slug *</p>
                <Input
                  value={createForm.slug}
                  onChange={(e) => setCreateForm((f) => ({ ...f, slug: e.target.value }))}
                  placeholder="bedtime-stories"
                  className="h-8 text-sm font-mono"
                />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-medium text-muted-foreground">Display order</p>
                <Input
                  type="number"
                  value={createForm.display_order}
                  onChange={(e) => setCreateForm((f) => ({ ...f, display_order: Number(e.target.value) }))}
                  className="h-8 text-sm w-20"
                />
              </div>
            </div>
            <div className="space-y-1">
              <p className="text-xs font-medium text-muted-foreground">Icon URL <span className="font-normal opacity-60">(optional)</span></p>
              <Input
                value={createForm.icon_url}
                onChange={(e) => setCreateForm((f) => ({ ...f, icon_url: e.target.value }))}
                placeholder="https://..."
                className="h-8 text-sm"
              />
            </div>
            <div className="space-y-2">
              <p className="text-xs font-medium text-muted-foreground">Translations</p>
              {createForm.translations.map((t, i) => (
                <div key={i} className="flex gap-2 items-center">
                  <Input
                    value={t.language}
                    onChange={(e) => setCreateTranslation(i, "language", e.target.value)}
                    placeholder="fa"
                    className="h-8 text-sm w-16 font-mono"
                  />
                  <Input
                    value={t.name}
                    onChange={(e) => setCreateTranslation(i, "name", e.target.value)}
                    placeholder="Name in that language"
                    className="h-8 text-sm flex-1"
                    dir={t.language === "fa" ? "rtl" : "ltr"}
                  />
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-8 w-8 shrink-0"
                    onClick={() => setCreateForm((f) => ({ ...f, translations: f.translations.filter((_, j) => j !== i) }))}
                  >
                    <X className="h-3.5 w-3.5" />
                  </Button>
                </div>
              ))}
              <Button
                size="sm"
                variant="outline"
                className="h-7 text-xs"
                onClick={() => setCreateForm((f) => ({ ...f, translations: [...f.translations, { language: "", name: "" }] }))}
              >
                <Plus className="h-3 w-3 mr-1" />Add translation
              </Button>
            </div>
            <div className="flex gap-2 pt-1">
              <Button size="sm" onClick={saveCreate} disabled={saving}>Save</Button>
              <Button size="sm" variant="outline" onClick={() => setCreating(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Slug</TableHead>
                <TableHead className="w-16">Order</TableHead>
                <TableHead>Translations</TableHead>
                <TableHead className="w-24" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && Array.from({ length: 4 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 4 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-full" /></TableCell>
                  ))}
                </TableRow>
              ))}
              {data?.results.map((cat: Category) => (
                <TableRow key={cat.id}>
                  {editing === cat.id ? (
                    <>
                      <TableCell>
                        <Input
                          value={editForm.slug}
                          onChange={(e) => setEditForm({ ...editForm, slug: e.target.value })}
                          className="h-8 text-sm w-36 font-mono"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={editForm.display_order}
                          onChange={(e) => setEditForm({ ...editForm, display_order: Number(e.target.value) })}
                          className="h-8 text-sm w-16"
                        />
                      </TableCell>
                      <TableCell>
                        <div className="space-y-1.5">
                          {langs.map((lang) => (
                            <div key={lang} className="flex gap-1.5 items-center">
                              <Badge variant="outline" className="text-xs w-7 justify-center shrink-0">{lang}</Badge>
                              <Input
                                value={editForm.translations.find((t) => t.language === lang)?.name ?? ""}
                                onChange={(e) => setEditTranslation(lang, e.target.value)}
                                className="h-7 text-xs"
                                dir={lang === "fa" ? "rtl" : "ltr"}
                                placeholder={`Name in ${lang}`}
                              />
                            </div>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 justify-end">
                          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => saveEdit(cat.id)} disabled={saving}>
                            <Check className="h-3.5 w-3.5 text-green-600" />
                          </Button>
                          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => setEditing(null)}>
                            <X className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell className="font-mono text-sm font-medium">{cat.slug}</TableCell>
                      <TableCell className="text-muted-foreground text-sm">{cat.display_order}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {cat.translations.map((t: CategoryTranslation) => (
                            <Badge key={t.language} variant="secondary" className="text-xs font-normal">
                              {t.language}: {t.name}
                            </Badge>
                          ))}
                          {cat.translations.length === 0 && (
                            <span className="text-xs text-muted-foreground italic">No translations</span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 justify-end">
                          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(cat)}>
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-7 w-7 text-destructive hover:text-destructive"
                            onClick={() => deleteCategory(cat.id)}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </TableCell>
                    </>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
