"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { getJobs } from "@/lib/api";
import type { Job } from "@/types";
import { JobCard, JobCardSkeleton } from "@/components/JobCard";

const SOURCES = [
  { label: "All sources", value: "" },
  { label: "HeadHunter", value: "headhunter" },
  { label: "Telegram", value: "telegram" },
];

const LOCATIONS = [
  { label: "All cities", value: "" },
  { label: "Алматы", value: "Алматы" },
  { label: "Астана", value: "Астана" },
  { label: "Remote", value: "Remote" },
];

export default function HomePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [q, setQ] = useState("");
  const [location, setLocation] = useState("");
  const [source, setSource] = useState("");

  const searchTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const activeQ = useRef("");
  const activeLocation = useRef("");
  const activeSource = useRef("");

  const fetchJobs = useCallback(
    async (
      query: string,
      loc: string,
      src: string,
      cur?: string
    ) => {
      const isLoadMore = !!cur;
      if (isLoadMore) setLoadingMore(true);
      else setLoading(true);
      setError(null);

      try {
        const data = await getJobs({
          q: query || undefined,
          location: loc || undefined,
          source: src || undefined,
          cursor: cur,
          limit: 20,
        });
        if (isLoadMore) {
          setJobs((prev) => [...prev, ...data.items]);
        } else {
          setJobs(data.items);
        }
        setCursor(data.next_cursor);
        setHasMore(data.has_more);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load jobs");
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    []
  );

  // Initial load
  useEffect(() => {
    fetchJobs("", "", "");
  }, [fetchJobs]);

  // Debounced search
  const triggerSearch = useCallback(
    (query: string, loc: string, src: string) => {
      if (searchTimer.current) clearTimeout(searchTimer.current);
      activeQ.current = query;
      activeLocation.current = loc;
      activeSource.current = src;
      searchTimer.current = setTimeout(() => {
        fetchJobs(query, loc, src);
      }, 350);
    },
    [fetchJobs]
  );

  const handleQChange = (v: string) => {
    setQ(v);
    triggerSearch(v, activeLocation.current, activeSource.current);
  };

  const handleLocationChange = (v: string) => {
    setLocation(v);
    triggerSearch(activeQ.current, v, activeSource.current);
  };

  const handleSourceChange = (v: string) => {
    setSource(v);
    triggerSearch(activeQ.current, activeLocation.current, v);
  };

  const clearSearch = () => {
    setQ("");
    setLocation("");
    setSource("");
    fetchJobs("", "", "");
  };

  const hasFilters = q || location || source;

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="space-y-2 pt-4">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-100">
          Tech jobs in Kazakhstan
        </h1>
        <p className="text-zinc-400">
          Aggregated from HeadHunter.kz and Telegram channels in real-time.
        </p>
      </div>

      {/* Search bar */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Search by title, company, or technology…"
            value={q}
            onChange={(e) => handleQChange(e.target.value)}
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 py-2.5 pl-9 pr-4 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <select
          value={location}
          onChange={(e) => handleLocationChange(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2.5 text-sm text-zinc-300 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        >
          {LOCATIONS.map((l) => (
            <option key={l.value} value={l.value}>
              {l.label}
            </option>
          ))}
        </select>

        <select
          value={source}
          onChange={(e) => handleSourceChange(e.target.value)}
          className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2.5 text-sm text-zinc-300 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        >
          {SOURCES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        {hasFilters && (
          <button
            onClick={clearSearch}
            className="flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2.5 text-sm text-zinc-400 transition hover:bg-zinc-800 hover:text-zinc-200"
          >
            <X className="h-3.5 w-3.5" />
            Clear
          </button>
        )}
      </div>

      {/* Results */}
      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 9 }).map((_, i) => (
            <JobCardSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <div className="rounded-xl border border-red-900/50 bg-red-950/20 p-8 text-center">
          <p className="text-red-400">{error}</p>
          <button
            onClick={() => fetchJobs(q, location, source)}
            className="mt-3 text-sm text-zinc-400 underline hover:text-zinc-200"
          >
            Try again
          </button>
        </div>
      ) : jobs.length === 0 ? (
        <div className="rounded-xl border border-zinc-800 p-12 text-center">
          <SlidersHorizontal className="mx-auto mb-3 h-8 w-8 text-zinc-600" />
          <p className="text-zinc-400">No jobs found</p>
          {hasFilters && (
            <button
              onClick={clearSearch}
              className="mt-2 text-sm text-indigo-400 hover:text-indigo-300"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-zinc-500">
              {jobs.length} job{jobs.length !== 1 ? "s" : ""} found
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>

          {hasMore && (
            <div className="flex justify-center pt-4">
              <button
                onClick={() =>
                  fetchJobs(
                    activeQ.current,
                    activeLocation.current,
                    activeSource.current,
                    cursor ?? undefined
                  )
                }
                disabled={loadingMore}
                className="rounded-lg border border-zinc-700 bg-zinc-900 px-6 py-2.5 text-sm text-zinc-300 transition hover:bg-zinc-800 hover:text-zinc-100 disabled:opacity-50"
              >
                {loadingMore ? "Loading…" : "Load more"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
