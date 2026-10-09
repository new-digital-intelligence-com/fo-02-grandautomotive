import { signedUrl } from "@/lib/elevenlabs";
import { allowCall, clientIp } from "@/lib/rateLimit";

/**
 * Starts a voice call with Katerina: returns a one-use signed WebSocket link. No login on this site, so each visitor may
 * start only a few calls (src/lib/rateLimit.ts). POST, so nothing caches or prefetches it.
 */
export async function POST(request: Request) {
  if (!allowCall(clientIp(request.headers))) {
    return Response.json({ error: "too_many_calls" }, { status: 429 });
  }
  try {
    return Response.json({ signedUrl: await signedUrl() });
  } catch (error) {
    console.error(error);
    return Response.json({ error: "Could not start a voice call" }, { status: 502 });
  }
}
