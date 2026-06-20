import { TrendingUp } from "lucide-react";
import { analytics } from "@/lib/api";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default async function AnalyticsPage() {
  const data = await analytics.get().catch(() => ({ top_stories: [] }));
  const topStory = data.top_stories[0];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Story view counts</p>
      </div>

      {/* Summary card */}
      {topStory && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Top story</CardDescription>
              <CardTitle className="text-lg font-mono">{topStory.story__slug}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <TrendingUp className="h-4 w-4 text-primary" />
                <span>{topStory.views.toLocaleString()} views</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total stories tracked</CardDescription>
              <CardTitle className="text-lg">{data.top_stories.length}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">with at least 1 view</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total views (top 10)</CardDescription>
              <CardTitle className="text-lg">
                {data.top_stories.reduce((s, r) => s + r.views, 0).toLocaleString()}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">across top stories</p>
            </CardContent>
          </Card>
        </div>
      )}

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Top 10 stories</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {data.top_stories.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground text-sm">
              No view data yet
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Story slug</TableHead>
                  <TableHead className="text-right">Views</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.top_stories.map((row, i) => (
                  <TableRow key={row.story__slug}>
                    <TableCell className="text-muted-foreground">{i + 1}</TableCell>
                    <TableCell className="font-mono text-sm">{row.story__slug}</TableCell>
                    <TableCell className="text-right">
                      <Badge variant={i === 0 ? "default" : "secondary"}>
                        {row.views.toLocaleString()}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
