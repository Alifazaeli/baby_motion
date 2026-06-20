/**
 * Polls /drafts/{id}/jobs/ every 3 seconds while any job is running/queued.
 * Stops polling once all jobs are in a terminal state (completed/failed).
 * Per OD-4: polling is the v1 mechanism; websockets/SSE can replace this later.
 */
import useSWR from "swr";
import type { GenerationJob } from "@/lib/types";
import { drafts } from "@/lib/api";

const POLL_INTERVAL_MS = 3000;

function isActive(job: GenerationJob) {
  return job.status === "queued" || job.status === "running";
}

export function useJobStatus(draftId: string | null) {
  const { data, error, mutate } = useSWR<GenerationJob[]>(
    draftId ? `jobs-${draftId}` : null,
    () => drafts.jobs(draftId!),
    {
      refreshInterval: (data) => {
        if (!data) return POLL_INTERVAL_MS;
        return data.some(isActive) ? POLL_INTERVAL_MS : 0;
      },
      revalidateOnFocus: false,
    }
  );

  const hasActive = data?.some(isActive) ?? false;
  const latestJob = data?.[0] ?? null;

  return { jobs: data ?? [], hasActive, latestJob, error, mutate };
}
