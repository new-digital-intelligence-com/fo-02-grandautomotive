/**
 * How many calls one visitor (IP address) may start. The site has no login, and every call spends ElevenLabs credits.
 * The agent itself also has a daily limit and a limit of calls at the same time (../agent/setup_agent.py, CALL_LIMITS).
 */
export const CALL_LIMITS = [
  { calls: 3, windowMs: 10 * 60 * 1000 },
  { calls: 10, windowMs: 24 * 60 * 60 * 1000 },
];

/**
 * Start times of recent calls per IP. Kept in the server's memory: on Vercel each instance has its own, so this slows
 * down a single visitor rather than enforcing an exact number.
 */
const recentCalls = new Map<string, number[]>();

/** Records a call start for this IP and says whether it is allowed. */
export function allowCall(ip: string, now = Date.now()): boolean {
  const longest = Math.max(...CALL_LIMITS.map((limit) => limit.windowMs));
  const times = (recentCalls.get(ip) ?? []).filter((time) => now - time < longest);
  const allowed = CALL_LIMITS.every((limit) => times.filter((time) => now - time < limit.windowMs).length < limit.calls);
  if (allowed) times.push(now);
  recentCalls.set(ip, times);
  if (recentCalls.size > 5000) forgetOldVisitors(now, longest);
  return allowed;
}

function forgetOldVisitors(now: number, longest: number) {
  for (const [ip, times] of recentCalls) {
    if (times.every((time) => now - time >= longest)) recentCalls.delete(ip);
  }
}

/** The visitor's IP as Vercel (or another proxy) reports it. */
export function clientIp(headers: Headers): string {
  const forwarded = headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  return forwarded || headers.get("x-real-ip") || "unknown";
}
