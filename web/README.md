# Grand Automotive – Greek voice assistant demo (web)

A public page where visitors talk to **Katerina**, the Greek voice assistant for Renault and Dacia in Greece (ElevenLabs agent
`agent_4601m465we6dfstbyq27zfsx8tqy`, set up by `../agent/setup_agent.py`). NDI demo, not an official Grand Automotive website.

- Greek by default, English switch. The switch also sets the call language (the agent's `en` preset).
- **No sign-up and no sign-in**: open the page, press the button, talk.
- The browser gets a one-use signed WebSocket link from `POST /api/voice/signed-url`; the ElevenLabs API key stays on the
  server. WebSocket, not WebRTC: over WebRTC the first tenth of a second of Katerina's greeting was cut (9 Oct 2026); the
  SDK keeps WebSocket audio that arrives early and plays it from the first sound. Both are billed the same, per minute.
- Credits are protected without a login:
  - the agent only accepts calls started with such a link (`enable_auth`), at most 4 at the same time and 50 a day, each up
    to 10 minutes (`../agent/setup_agent.py`);
  - each visitor (IP) may start 3 calls per 10 minutes and 10 a day (`src/lib/rateLimit.ts`, kept in the server's memory, so on
    Vercel it slows a visitor down rather than counting exactly).
- The transcript shows phone numbers whole (Katerina says them digit by digit) and prices with the usual separator
  (`src/components/transcriptText.ts`).

## Run locally

```bash
npm install
cp .env.example .env.local   # then fill in the 2 values
npm run dev                  # http://localhost:3000
```

## Deploy on Vercel

1. New project → import the repository. Set **Root Directory** to `web`.
2. Framework preset: Next.js (detected). No build settings to change.
3. Environment variables:

| Name | Value |
|---|---|
| `ELEVENLABS_API_KEY` | The ElevenLabs API key (same account as the agent) |
| `ELEVENLABS_AGENT_ID` | `agent_4601m465we6dfstbyq27zfsx8tqy` |

4. Deploy. After changing a variable later, redeploy.

Checks before deploying: `npm run build`, `npx tsc --noEmit`, `npm run lint`.
