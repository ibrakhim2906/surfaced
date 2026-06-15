"use client";

import Link from "next/link";
import { Bookmark, Briefcase, LogOut, User } from "lucide-react";
import { useAuth } from "./AuthProvider";

export function Navbar() {
  const { user, logout, loading } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link
          href="/"
          className="flex items-center gap-2 text-lg font-semibold tracking-tight text-zinc-100 hover:text-white"
        >
          <Briefcase className="h-5 w-5 text-indigo-400" />
          Surfaced
        </Link>

        <nav className="flex items-center gap-1">
          <Link
            href="/"
            className="rounded-md px-3 py-1.5 text-sm text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-100"
          >
            Jobs
          </Link>

          {!loading && user && (
            <Link
              href="/saved"
              className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-100"
            >
              <Bookmark className="h-3.5 w-3.5" />
              Saved
            </Link>
          )}

          {!loading && (
            <>
              {user ? (
                <div className="ml-2 flex items-center gap-2">
                  <span className="flex items-center gap-1.5 rounded-full border border-zinc-800 bg-zinc-900 px-3 py-1 text-sm text-zinc-300">
                    <User className="h-3 w-3 text-zinc-500" />
                    {user.full_name}
                  </span>
                  <button
                    onClick={logout}
                    className="rounded-md p-1.5 text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-300"
                    title="Sign out"
                  >
                    <LogOut className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="ml-2 flex items-center gap-2">
                  <Link
                    href="/auth/login"
                    className="rounded-md px-3 py-1.5 text-sm text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-100"
                  >
                    Sign in
                  </Link>
                  <Link
                    href="/auth/register"
                    className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500"
                  >
                    Sign up
                  </Link>
                </div>
              )}
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
