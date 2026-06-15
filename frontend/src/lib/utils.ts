export function formatSalary(
  min: number | null,
  max: number | null
): string | null {
  if (!min && !max) return null;
  const fmt = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${Math.round(n / 1_000)}K`;
    return n.toLocaleString();
  };
  if (min && max) return `${fmt(min)} – ${fmt(max)} ₸`;
  if (min) return `от ${fmt(min)} ₸`;
  return `до ${fmt(max!)} ₸`;
}

export function formatTimeAgo(dateStr: string | null): string {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60_000);
  const hours = Math.floor(diff / 3_600_000);
  const days = Math.floor(diff / 86_400_000);
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

const BADGE_COLORS = [
  "bg-blue-500/10 text-blue-400 border border-blue-500/20",
  "bg-violet-500/10 text-violet-400 border border-violet-500/20",
  "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
  "bg-amber-500/10 text-amber-400 border border-amber-500/20",
  "bg-rose-500/10 text-rose-400 border border-rose-500/20",
  "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20",
  "bg-orange-500/10 text-orange-400 border border-orange-500/20",
  "bg-pink-500/10 text-pink-400 border border-pink-500/20",
];

export function techBadgeColor(tech: string): string {
  let hash = 0;
  for (const c of tech) hash = (hash * 31 + c.charCodeAt(0)) & 0xffff;
  return BADGE_COLORS[hash % BADGE_COLORS.length];
}

export function cn(...classes: (string | undefined | false | null)[]): string {
  return classes.filter(Boolean).join(" ");
}
