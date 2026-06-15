"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  MapPin,
  Send,
} from "lucide-react";
import { getJob } from "@/lib/api";
import { formatSalary, formatTimeAgo, techBadgeColor } from "@/lib/utils";
import { useAuth } from "@/components/AuthProvider";
import type { Job } from "@/types";

export default function JobDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { savedJobIds, toggleSave } = useAuth();

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFull, setShowFull] = useState(false);

  useEffect(() => {
    getJob(Number(id))
      .then(setJob)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl space-y-6 animate-pulse">
        <div className="h-4 w-24 rounded bg-zinc-800" />
        <div className="space-y-3">
          <div className="h-8 w-2/3 rounded bg-zinc-800" />
          <div className="h-4 w-1/3 rounded bg-zinc-800" />
        </div>
        <div className="h-64 rounded-xl bg-zinc-800" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="mx-auto max-w-2xl text-center py-20">
        <p className="text-zinc-400">{error ?? "Job not found"}</p>
        <button
          onClick={() => router.back()}
          className="mt-4 text-sm text-indigo-400 hover:text-indigo-300"
        >
          Go back
        </button>
      </div>
    );
  }

  const isSaved = savedJobIds.has(job.id);
  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency);
  const timeAgo = formatTimeAgo(job.posted_at);
  const PREVIEW_LENGTH = 600;
  const longDesc = job.description.length > PREVIEW_LENGTH;
  const displayedDesc =
    showFull || !longDesc
      ? job.description
      : job.description.slice(0, PREVIEW_LENGTH) + "…";

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1.5 text-sm text-zinc-500 transition hover:text-zinc-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to jobs
      </button>

      {/* Header card */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 space-y-4">
        {/* Source + time */}
        <div className="flex items-center gap-2 flex-wrap">
          {job.source === "telegram" ? (
            <span className="flex items-center gap-1 rounded-full bg-blue-500/10 px-2.5 py-0.5 text-xs font-medium text-blue-400 border border-blue-500/20">
              <Send className="h-2.5 w-2.5" />
              Telegram
            </span>
          ) : (
            <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-500/20">
              HH.kz
            </span>
          )}
          {timeAgo && (
            <span className="text-xs text-zinc-500">{timeAgo}</span>
          )}
        </div>

        {/* Title + company */}
        <div>
          <h1 className="text-2xl font-bold text-zinc-100 leading-snug">
            {job.title}
          </h1>
          <p className="mt-1 text-zinc-400">{job.company}</p>
        </div>

        {/* Meta row */}
        <div className="flex flex-wrap gap-4 text-sm">
          {job.location && (
            <span className="flex items-center gap-1.5 text-zinc-400">
              <MapPin className="h-3.5 w-3.5 text-zinc-600" />
              {job.location}
            </span>
          )}
          {salary && (
            <span className="font-medium text-indigo-400">{salary}</span>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-1">
          <a
            href={job.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500"
          >
            Apply
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
          <button
            onClick={() => toggleSave(job.id)}
            className="flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm text-zinc-300 transition hover:bg-zinc-700"
          >
            {isSaved ? (
              <>
                <BookmarkCheck className="h-4 w-4 text-indigo-400" />
                Saved
              </>
            ) : (
              <>
                <Bookmark className="h-4 w-4" />
                Save
              </>
            )}
          </button>
        </div>
      </div>

      {/* Tech stack */}
      {job.stack.length > 0 && (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 space-y-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
            Tech stack
          </h2>
          <div className="flex flex-wrap gap-2">
            {job.stack.map((tech) => (
              <span
                key={tech}
                className={`rounded-md px-2.5 py-1 text-sm font-medium ${techBadgeColor(tech)}`}
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Description */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5 space-y-3">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
          Description
        </h2>
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">
          {displayedDesc}
        </p>
        {longDesc && (
          <button
            onClick={() => setShowFull((v) => !v)}
            className="text-sm text-indigo-400 hover:text-indigo-300"
          >
            {showFull ? "Show less" : "Show more"}
          </button>
        )}
      </div>
    </div>
  );
}
