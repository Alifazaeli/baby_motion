"use client";
import useSWR from "swr";
import { toast } from "sonner";
import { languages } from "@/lib/api";
import type { Language } from "@/lib/types";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function LanguagesPage() {
  const { data, isLoading, mutate } = useSWR("languages", () => languages.list());

  async function toggleActive(lang: Language) {
    try {
      await languages.update(lang.code, { is_active: !lang.is_active });
      await mutate();
      toast.success(`${lang.display_name} ${!lang.is_active ? "enabled" : "disabled"}`);
    } catch {
      toast.error("Failed to update language");
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Languages</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Active languages are available for story generation and client apps.
          Adding a new row is all that's needed to support a new language system-wide.
        </p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">Code</TableHead>
                <TableHead>Display name</TableHead>
                <TableHead>Direction</TableHead>
                <TableHead>Active</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading && Array.from({ length: 2 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 4 }).map((_, j) => (
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
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
