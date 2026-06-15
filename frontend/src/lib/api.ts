import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "./auth";
import type {
  Job,
  ListSavedJobs,
  PaginatedJobs,
  SavedJob,
  TokenResponse,
  User,
} from "@/types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

let refreshing: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_URL}/api/v1/auth/token/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data: TokenResponse = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

async function apiFetch<T>(
  path: string,
  init?: RequestInit,
  retry = true
): Promise<T> {
  const token = getAccessToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });

  if (res.status === 401 && retry) {
    if (!refreshing) refreshing = tryRefresh().finally(() => (refreshing = null));
    const ok = await refreshing;
    if (ok) return apiFetch<T>(path, init, false);
    clearTokens();
    if (typeof window !== "undefined") window.location.href = "/auth/login";
    throw new Error("Session expired");
  }

  if (res.status === 204) return undefined as T;

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail ?? "Request failed");
  }

  return res.json();
}

// Auth
export async function register(
  full_name: string,
  email: string,
  password: string
): Promise<User> {
  return apiFetch("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ full_name, email, password }),
  });
}

export async function login(
  email: string,
  password: string
): Promise<TokenResponse> {
  return apiFetch("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(refresh_token: string): Promise<void> {
  return apiFetch("/api/v1/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

export async function getMe(): Promise<User> {
  return apiFetch("/api/v1/auth/me");
}

// Jobs
export interface JobsParams {
  q?: string;
  location?: string;
  source?: string;
  limit?: number;
  cursor?: string;
}

export async function getJobs(params: JobsParams = {}): Promise<PaginatedJobs> {
  const qs = new URLSearchParams();
  if (params.q) qs.set("q", params.q);
  if (params.location) qs.set("location", params.location);
  if (params.source) qs.set("source", params.source);
  if (params.limit) qs.set("limit", String(params.limit));
  if (params.cursor) qs.set("cursor", params.cursor);
  return apiFetch(`/api/v1/jobs?${qs}`);
}

export async function getJob(id: number): Promise<Job> {
  return apiFetch(`/api/v1/jobs/${id}`);
}

// Saved jobs
export async function getSavedJobs(): Promise<ListSavedJobs> {
  return apiFetch("/api/v1/jobs/me/saved");
}

export async function saveJob(job_id: number): Promise<SavedJob> {
  return apiFetch("/api/v1/jobs/me/saved", {
    method: "POST",
    body: JSON.stringify({ job_id }),
  });
}

export async function unsaveJob(job_id: number): Promise<void> {
  return apiFetch(`/api/v1/jobs/me/saved/${job_id}`, { method: "DELETE" });
}
