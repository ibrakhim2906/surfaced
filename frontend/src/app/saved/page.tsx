"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Bookmark } from "lucide-react";
import { getSavedJobs } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { JobCard, JobCardSkeleton } from "@/components/JobCard";
import type { Job } from "@/types";

export default function SavedPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/auth/login");
      return;
    }
    getSavedJobs()
      .then(({ items }) => setJobs(items.map((s) => s.job)))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">Saved jobs</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Jobs you&apos;ve bookmarked for later
        </p>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <JobCardSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-8 text-center">
          <p className="text-red-400">{error}</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="rounded-xl border border-zinc-800 p-16 text-center">
          <Bookmark className="mx-auto mb-3 h-8 w-8 text-zinc-700" />
          <p className="text-zinc-400">No saved jobs yet</p>
          <p className="mt-1 text-sm text-zinc-600">
            Bookmark jobs from the listing to find them here
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
