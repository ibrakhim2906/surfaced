export interface Job {
  id: number;
  title: string;
  company: string;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  description: string;
  stack: string[];
  source: string;
  source_url: string;
  posted_at: string | null;
  is_archived: boolean;
}

export interface PaginatedJobs {
  items: Job[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SavedJob {
  id: number;
  user_id: number;
  job_id: number;
  saved_at: string;
  job: Job;
}

export interface ListSavedJobs {
  items: SavedJob[];
}
