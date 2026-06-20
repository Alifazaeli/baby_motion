"use client";
import { useState } from "react";
import useSWR from "swr";
import { Pencil, Trash2, Check, X } from "lucide-react";
import { toast } from "sonner";
import { categories } from "@/lib/api";
import type { Category } from "@/lib/types";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function CategoriesPage() {
  const { data, isLoading, mutate } = useSWR("categories", () => categories.list());
  const [editing, setEditing] = useState<string | null>(null);
  const [form, setForm] = useState({ slug: "", icon_url: "", display_order: 0 });
  const [saving, setSaving] = useState(false);

  async function startEdit(cat: Category) {
    setEditing(cat.id);
    setForm({ slug: cat.slug, icon_url: cat.icon_url, display_order: cat.display_order });
  }

  async function saveEdit(id: string) {
    setSaving(true);
    try {
      await categories.update(id, form);
      await mutate();
      setEditing(null);
      toast.success("Category updated");
    } catch {
      toast.error("Failed to update category");
    } finally {
      setSaving(false);
    }
  }

  async function deleteCategory(id: string) {
    if (!confirm("Delete this category? Stories using it cannot be deleted.")) return;
    try {
      await categories.delete(id);
      await mutate();
      toast.success("Category deleted");
    } catch {
      toast.error("Failed to delete category");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Categories</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Manage story categories</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Slug</TableHead>
                <TableHead>Order</TableHead>
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
                          value={form.slug}
                          onChange={(e) => setForm({ ...form, slug: e.target.value })}
                          className="h-8 text-sm w-36"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={form.display_order}
                          onChange={(e) => setForm({ ...form, display_order: Number(e.target.value) })}
                          className="h-8 text-sm w-16"
                        />
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {cat.translations.map((t) => `${t.language}: ${t.name}`).join(", ")}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
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
                          {cat.translations.map((t) => (
                            <Badge key={t.language} variant="secondary" className="text-xs font-normal">
                              {t.language}: {t.name}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 justify-end">
                          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => startEdit(cat)}>
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button size="icon" variant="ghost" className="h-7 w-7 text-destructive hover:text-destructive" onClick={() => deleteCategory(cat.id)}>
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
