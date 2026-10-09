const API_BASE = "https://api.elevenlabs.io/v1/convai";

function credentials() {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  const agentId = process.env.ELEVENLABS_AGENT_ID;
  if (!apiKey || !agentId) {
    throw new Error("ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID must be set");
  }
  return { apiKey, agentId };
}

/**
 * A one-use signed WebSocket link for a voice call with Katerina. The browser starts the call with it and never sees the
 * API key. The agent only accepts calls started with such a link (enable_auth, set by ../agent/setup_agent.py).
 *
 * WebSocket, not WebRTC: over WebRTC Katerina starts speaking before the browser plays the call's audio track, which cut
 * the first tenth of a second of her greeting («Γεια σας»). Over WebSocket the SDK keeps audio that arrives early and plays
 * it from the first sound. Both are billed the same, per minute of call.
 */
export async function signedUrl(): Promise<string> {
  const { apiKey, agentId } = credentials();
  // include_conversation_id makes the link usable once, like the WebRTC token was
  const query = new URLSearchParams({ agent_id: agentId, include_conversation_id: "true" });
  const response = await fetch(`${API_BASE}/conversation/get-signed-url?${query}`, {
    headers: { "xi-api-key": apiKey },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`ElevenLabs signed URL failed with ${response.status}`);
  }
  const body = (await response.json()) as { signed_url: string };
  return body.signed_url;
}
