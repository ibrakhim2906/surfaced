"use client";

import Link from "next/link";
import { Bookmark, BookmarkCheck, MapPin, Send } from "lucide-react";
import { formatSalary, formatTimeAgo, techBadgeColor } from "@/lib/utils";
import type { Job } from "@/types";
import { useAuth } from "./AuthProvider";

const MAX_BADGES = 4;

function SourceBadge({ source }: { source: string }) {
  if (source === "telegram") {
    return (
      <span className="flex items-center gap-1 rounded-full bg-blue-500/10 px-2 py-0.5 text-xs font-medium text-blue-400 border border-blue-500/20">
        <Send className="h-2.5 w-2.5" />
        Telegram
      </span>
    );
  }
  return (
    <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-500/20">
      HH.kz
    </span>
  );
}

export function JobCard({ job }: { job: Job }) {
  const { savedJobIds, toggleSave } = useAuth();
  const isSaved = savedJobIds.has(job.id);
  const salary = formatSalary(job.salary_min, job.salary_max);
  const timeAgo = formatTimeAgo(job.posted_at);
  const visibleStack = job.stack.slice(0, MAX_BADGES);
  const extraCount = job.stack.length - MAX_BADGES;

  return (
    <div className="group relative flex flex-col gap-3 rounded-xl border border-zinc-800 bg-zinc-900 p-5 transition-all hover:border-zinc-700 hover:bg-zinc-800/60">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <SourceBadge source={job.source} />
          {job.location && (
            <span className="flex items-center gap-1 text-xs text-zinc-500">
              <MapPin className="h-3 w-3" />
              {job.location}
            </span>
          )}
        </div>
        <button
          onClick={(e) => {
            e.preventDefault();
            toggleSave(job.id);
          }}
          className="shrink-0 rounded-md p-1.5 text-zinc-600 transition-colors hover:bg-zinc-700 hover:text-zinc-300"
          aria-label={isSaved ? "Unsave job" : "Save job"}
        >
          {isSaved ? (
            <BookmarkCheck className="h-4 w-4 text-indigo-400" />
          ) : (
            <Bookmark className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* Title + company */}
      <Link href={`/jobs/${job.id}`} className="block">
        <h2 className="text-base font-semibold text-zinc-100 group-hover:text-white line-clamp-2 leading-snug">
          {job.title}
        </h2>
        <p className="mt-1 text-sm text-zinc-400">{job.company}</p>
      </Link>

      {/* Salary */}
      {salary && (
        <p className="text-sm font-medium text-indigo-400">{salary}</p>
      )}

      {/* Stack + time */}
      <div className="mt-auto flex items-end justify-between gap-2 pt-1">
        <div className="flex flex-wrap gap-1.5">
          {visibleStack.map((tech) => (
            <span
              key={tech}
              className={`rounded-md px-2 py-0.5 text-xs font-medium ${techBadgeColor(tech)}`}
            >
              {tech}
            </span>
          ))}
          {extraCount > 0 && (
            <span className="rounded-md px-2 py-0.5 text-xs text-zinc-500 border border-zinc-700">
              +{extraCount}
            </span>
          )}
        </div>
        {timeAgo && (
          <span className="shrink-0 text-xs text-zinc-600">{timeAgo}</span>
        )}
      </div>
    </div>
  );
}

export function JobCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-zinc-800 bg-zinc-900 p-5 animate-pulse">
      <div className="flex gap-2">
        <div className="h-5 w-16 rounded-full bg-zinc-800" />
        <div className="h-5 w-20 rounded-full bg-zinc-800" />
      </div>
      <div className="space-y-2">
        <div className="h-4 w-3/4 rounded bg-zinc-800" />
        <div className="h-3 w-1/3 rounded bg-zinc-800" />
      </div>
      <div className="h-3 w-1/4 rounded bg-zinc-800" />
      <div className="flex gap-2">
        <div className="h-5 w-14 rounded-md bg-zinc-800" />
        <div className="h-5 w-14 rounded-md bg-zinc-800" />
        <div className="h-5 w-14 rounded-md bg-zinc-800" />
      </div>
    </div>
  );
}
