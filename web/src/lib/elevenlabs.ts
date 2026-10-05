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
 * A one-use WebRTC token for a voice call with Katerina. The browser starts the call with it and never sees the API key.
 * The agent only accepts calls started with such a token (enable_auth, set by ../agent/setup_agent.py).
 */
export async function conversationToken(): Promise<string> {
  const { apiKey, agentId } = credentials();
  const response = await fetch(`${API_BASE}/conversation/token?${new URLSearchParams({ agent_id: agentId })}`, {
    headers: { "xi-api-key": apiKey },
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`ElevenLabs conversation token failed with ${response.status}`);
  }
  const body = (await response.json()) as { token: string };
  return body.token;
}
