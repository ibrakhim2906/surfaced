"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import * as api from "@/lib/api";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "@/lib/auth";
import type { User } from "@/types";

interface AuthContext {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  savedJobIds: Set<number>;
  toggleSave: (jobId: number) => Promise<void>;
  refreshSaved: () => Promise<void>;
}

const Ctx = createContext<AuthContext | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [savedJobIds, setSavedJobIds] = useState<Set<number>>(new Set());

  const refreshSaved = useCallback(async () => {
    if (!getAccessToken()) return;
    try {
      const { items } = await api.getSavedJobs();
      setSavedJobIds(new Set(items.map((s) => s.job_id)));
    } catch {
      // silent — user may have just logged out
    }
  }, []);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getMe()
      .then(async (u) => {
        setUser(u);
        await refreshSaved();
      })
      .catch(() => {
        clearTokens();
      })
      .finally(() => setLoading(false));
  }, [refreshSaved]);

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await api.login(email, password);
      setTokens(tokens.access_token, tokens.refresh_token);
      const u = await api.getMe();
      setUser(u);
      await refreshSaved();
    },
    [refreshSaved]
  );

  const logout = useCallback(async () => {
    const refresh = getRefreshToken();
    if (refresh) await api.logout(refresh).catch(() => {});
    clearTokens();
    setUser(null);
    setSavedJobIds(new Set());
  }, []);

  const toggleSave = useCallback(
    async (jobId: number) => {
      if (!user) {
        window.location.href = "/auth/login";
        return;
      }
      const saved = savedJobIds.has(jobId);
      // Optimistic update
      setSavedJobIds((prev) => {
        const next = new Set(prev);
        saved ? next.delete(jobId) : next.add(jobId);
        return next;
      });
      try {
        if (saved) {
          await api.unsaveJob(jobId);
        } else {
          await api.saveJob(jobId);
        }
      } catch {
        // Rollback
        setSavedJobIds((prev) => {
          const next = new Set(prev);
          saved ? next.add(jobId) : next.delete(jobId);
          return next;
        });
      }
    },
    [user, savedJobIds]
  );

  return (
    <Ctx.Provider
      value={{ user, loading, login, logout, savedJobIds, toggleSave, refreshSaved }}
    >
      {children}
    </Ctx.Provider>
  );
}

export function useAuth(): AuthContext {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
