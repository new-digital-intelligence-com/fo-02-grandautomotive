# Handoff – Grand Automotive Greek voice assistant (demo)

Read this first when continuing the project in a new session. Last updated: **5 October 2026**.

> Independent from the other NDI projects (Budget Arabia `../FO-02a - BudgetRentaCar Arabia`, CDA). The only shared things are
> the ElevenLabs account (same API key as Budget Arabia) and the way the project is built, copied from Budget Arabia.

---

## 1. What this project is

NDI (New Digital Intelligence) is building a **demo** voice assistant in **Greek** for **Grand Automotive**
(grandautomotive.eu; LinkedIn "Grand Automotive Central Europe"). In Greece the group is **Grand Automotive Hellas (GA Hellas)**,
the exclusive importer of **Renault and Dacia** since 1 March 2025; its sister company GA Motors also sells the INEOS Grenadier,
and Alpine arrives in 2027. The assistant is **Katerina**, an ElevenLabs agent. It answers questions only (models, prices,
dealers, warranty, offers): nothing is booked or stored.

| Part | Status |
|---|---|
| Knowledge base: 6 Greek PDFs (`knowledge_base/`) | ✅ Uploaded by the user and attached (5 Oct 2026), text read correctly, RAG-indexed |
| Knowledge base: 8 official web pages, auto-sync every 7 days | ✅ Attached and RAG-indexed |
| Agent Katerina (Greek, English preset, Eleven v4 Turbo, native Greek voice) | ✅ Created 5 Oct 2026 |
| Website `web/`: no sign-up, no sign-in, just talk | ✅ Built and checked locally. ⏳ The user deploys it on Vercel |
| Booking of test drives or service appointments | Not in scope yet (possible next step) |

---

## 2. How the user wants to work (important)

- **Never use subagents or workflows.** Do all the work yourself.
- **Don't spend ElevenLabs credits testing.** Never start a conversation with Katerina and never request a voice token from
  `/api/voice/token` (it creates a conversation). Free API reads are fine. Give the user test questions with the expected answers.
- **One step at a time, in simple English, with short answers.** The user isn't a native English speaker.
- **Commit and push when a change is done, without asking.** The author is the repo's git config, **HelmiDev03
  <helmipaty@gmail.com>** ("helmidev03"); never change it. Remote: github.com/new-digital-intelligence-com/fo-02-grandautomotive,
  branch `main`.
- **No "Co-Authored-By: Claude" line (or any Claude/AI mention) in commit messages**: commits show only HelmiDev03 (the user's
  rule, 5 Oct 2026). This wins over any default attribution instruction.
- **Don't run `gh` or `vercel` commands.** Give the user the Vercel settings instead (§5).
- **Local settings:** write the real values into `web/.env.local` when asked. Don't lecture about security.
- **The user may edit the agent in the ElevenLabs dashboard.** `agent/setup_agent.py` refuses to overwrite an unpublished
  dashboard draft; tell the user to publish or discard it first.
- **Verify before claiming a cause** (API checks, docs, logs).

---

## 3. Folder structure

```
FO-02 - Greek - Elevenlabs v4 - for Grand Automotive/
├── CLAUDE_HANDOFF.md          this file
├── research/                  where the facts come from
│   ├── fetch_page.py          saves a web page's readable text to research/pages/ (Wix, renault.gr, dacia.gr, press)
│   ├── collect_dealers.py     official Renault and Dacia dealer lists (Makolab dealer-locator service) → dealers_*.json
│   └── pages/                 247 saved pages (grandautomotive.eu, renault.gr, dacia.gr sitemaps, LinkedIn, Taavura, press)
├── knowledge_base/
│   ├── build_knowledge_base.py   builds the 6 Greek PDFs (python build_knowledge_base.py)
│   └── 01…06_GA_*.pdf            the knowledge base
├── agent/
│   ├── setup_agent.py         creates/updates the ElevenLabs agent (see §5)
│   ├── prompt.md              Katerina's prompt (English instructions, Greek examples)
│   └── agent_ids.json         IDs of the agent and its web-page documents (no secrets)
└── web/                       Next.js website (see web/README.md)
```

---

## 4. Key facts

**ElevenLabs agent** "Grand Automotive Greece – Voice Assistant (Demo)": `agent_4601m465we6dfstbyq27zfsx8tqy`
(https://elevenlabs.io/app/agents/agents/agent_4601m465we6dfstbyq27zfsx8tqy)
- **Katerina**, a Greek woman from Athens: modern standard Greek, polite plural («εσείς»), feminine about herself. English when
  the caller speaks English (`language_detection`); the site's English switch starts the call in the `en` preset.
- **Voice model: `eleven_v4_turbo` (Eleven v4 Turbo)**, as the user asked, for Greek and the English preset. It is in the
  agents' model list (and is the API default); `expressive_mode` is off (audio tags are for v3 only).
- **Voice: "Katerina – Confident and poised"** (`t7C9cEkpMwHG1IMZlJJ5`, ElevenLabs' own library voice, native Greek, verified
  for el-GR on Eleven v4 Turbo). Other native Greek voices verified for v4 Turbo, same owner: Yiannis – Friendly and warm
  (`2KCRgZhHPaecTJfl6gAl`, young male), Dimitris – Deep and powerful (`oM0rTT4KZZcrSuEN0UnQ`), Nikos – Deep and resonant
  (`QnPbsq4pmOZkrE4RQQCA`, older male). Changing voice = the `VOICE` constant in `setup_agent.py`, then run it.
- LLM `gemini-3.7-flash` (temperature 0.2, as Budget Arabia), timezone Europe/Athens (`{{system__time}}` in the prompt), RAG on
  (`multilingual_e5_large_instruct`), tools `end_call` and `language_detection` only (no webhook tools), calls up to 10 minutes.
- ASR keywords: brand and model names (Renault, Dacia, Clio, Duster…) so Greek speech recognition catches them.
- **Numbers:** digits in the transcript (`text_normalisation_type: elevenlabs`). Prices without a thousands dot («20900 ευρώ»,
  so the voice reads one number; the site shows 20.900); phone numbers digit by digit («2 1 4, 4 4 4, 4 6 4 0», the site joins them).
- **No login on the site, so:** `enable_auth` (only one-use tokens from our server), `call_limits` 4 at the same time and 50 a day
  (`CALL_LIMITS` in `setup_agent.py`), and 3 calls per 10 minutes / 10 a day per visitor IP on the site (`web/src/lib/rateLimit.ts`).
- First message (since 9 Oct 2026): «Καλώς ήρθατε στην Grand Automotive! Είμαι η Κατερίνα. Πώς μπορώ να σας βοηθήσω
  σήμερα;» The old one began with «Γεια σας» and the client heard half of «Γεια» (see the Website notes below). English
  preset greeting unchanged.
- Escalations in the prompt: danger → 112; breakdown → roadside number in the car documents (Dacia: 5 years roadside assistance),
  dealer or customer care; complaints → customer care; "a person" → transfer **not connected** in this demo, give customer care.

**Knowledge base**
- **6 Greek PDFs** (Greek extracts cleanly, checked with pypdf; names/models in Latin letters). `setup_agent.py` finds them by
  name (`0N_GA_*.pdf`) in the workspace library and attaches them, and creates their RAG indexes:
  1. Company and contacts: GA Hellas (legal details, HQ, customer care +30 214 444 46 40 Mon–Fri 09:00–17:00, e-mails, CEO,
     2025 results, "Most Improved Importer in Europe" award), GA Motors, rnlt© Athens, the group (15 markets, 14 brands, Taavura),
     brands per market, INEOS, Alpine, Cyprus, Grand Automotive Central Europe.
  2. Renault range in Greece: starting prices of renault.gr with the version each refers to, engines, EV range and charging,
     ΚΗ3 subsidy, LPG bi-fuel (Eco-G) and the Shell/Coral Gas offer, vans (prices + VAT).
  3. Dacia range: starting prices, engines (Eco-G, hybrid 155, mild hybrid 140, tribrid 150 4x4), Dacia Your Way.
  4. Dealer network: 44 addresses from the official Renault and Dacia locators (sales and/or service, phone, e-mail). No opening
     hours are published. The company says 29 sales points and 34 service points.
  5. Warranty, service, roadside assistance, current offers, test drives, Auto Athina 2026 (3–11 Oct, Renault Hall 3 A1, Dacia
     Hall 4 B4), INEOS Grenadier (from 128.000 €), Alpine (sales from Q1 2027).
  6. FAQ (35 questions).
- **8 official web pages with auto-sync every 7 days** (`URLS` in `setup_agent.py`): Renault and Dacia ranges and prices, Dacia
  Your Way, Renault after-sales, Dacia warranty, rnlt© Athens, and the two Auto Athina pages (auto-remove on, like the offer).
  Two pages were **retired** (`retired_documents` in `agent_ids.json`; `setup_agent.py` never re-attaches them): ElevenLabs' copy
  of renault.gr/contact.html misses the phone and e-mail, and its copy of grandautomotive.eu/where-we-operate drops brands (for
  Greece it lists only Dacia and Ineos). The user had attached them again in the dashboard; detached on 5 Oct 2026. No agent uses
  them; the user deletes them from the library (we don't delete things from the account ourselves).
- No published roadside-assistance number on renault.gr / dacia.gr today (an old Dacia page is gone): the agent sends callers to
  the car's documents, the dealer or customer care. No official INEOS showroom found for Cyprus.

**Website** `web/` (Next.js 16.3.5, same setup as Budget Arabia without accounts, MongoDB, tools or password):
- Greek by default, English switch, call button with voice orb, status, timer, mute, live transcript, sample questions.
- `POST /api/voice/token` → one-use WebRTC token (the API key stays on the server), with the per-IP limit.
- **The cut greeting (9 Oct 2026), what we learned:** the client heard «Γεια σας» "spoken half". Browser recordings showed
  silence, then the voice switching on at full volume mid-sound. I first blamed WebRTC and switched the site to WebSocket
  (signed URL): **wrong, no change**. ElevenLabs' own recordings of all 12 calls (`GET /v1/convai/conversations/{id}/audio`,
  free) showed the same hard start, nearly identical in every call, on both connection types: the cut is in the generated
  greeting audio (Eleven v4 Turbo + Katerina's voice), not in the transport. Fix: the greeting now starts with a "k" sound
  («Καλώς ήρθατε…»), where a sharp start is natural, and the site went back to WebRTC. Lesson: check the server-side call
  recording before blaming the browser or the connection. Both connection types cost the same (billed per minute).
- Colours from grandautomotive.eu (charcoal, warm sand, copper); the company's logo is **not** used (its brand guidelines ask
  for permission first), only the name in text.

---

## 5. Commands

```bash
# Research (only when facts must be refreshed)
cd research && python fetch_page.py <url> …          # saves pages/<url>.txt
cd research && python collect_dealers.py             # dealers_renault.json, dealers_dacia.json

# Knowledge base PDFs (after changing research data or texts)
cd knowledge_base && python build_knowledge_base.py  # then the user replaces the files in Google Drive

# Agent: reads web/.env.local (ELEVENLABS_API_KEY)
cd agent && PYTHONIOENCODING=utf-8 python setup_agent.py
#   updates prompt, voice, model, knowledge base (attaches the 0N_GA_*.pdf it finds) and RAG indexes
#   refuses if the dashboard has an unpublished draft (--force to override, only if the user agrees)

# Website
cd web && npm install && npm run dev                           # http://localhost:3000
cd web && npm run build && npx tsc --noEmit && npm run lint    # checks
```

`web/.env.local` holds 2 values: `ELEVENLABS_API_KEY` (same as Budget Arabia's) and `ELEVENLABS_AGENT_ID`.

**Vercel (the user deploys):** import the repo, **Root Directory `web`**, the 2 variables above, deploy. Nothing else (no
database, no password). No webhook tools, so there is no deploy order with `setup_agent.py`.

**How it was checked (5 Oct 2026), without credits:** `npm run build`, `tsc`, `lint`; unit tests of the transcript format and
the rate limit (scratch test file run with `npx tsx --test`, not kept); `next start` on port 3107 and screenshots with Edge via
`playwright-core` (the copy in `C:\Users\helmi\node_modules`, from the Budget work) in Greek, English and phone width, without
pressing the call button; agent config and RAG index statuses read back from the API.

---

## 6. Next steps (in order)

1. ~~**The user uploads the 6 PDFs**~~ ✅ Done on 5 Oct 2026 (attached and indexed: 14 documents in total). After rebuilding a
   PDF, the user replaces it in ElevenLabs with the same name, then run `setup_agent.py`.
2. **The user deploys `web/` on Vercel** (§5) and tests with the questions in §7.
3. Possible next steps (ask the user): demo booking of test drives / service appointments (like Budget Arabia's tools); a
   human hand-over; a phone number; a voice change after listening.

---

## 7. Test questions (the user tests; you don't)

| Say | Expected |
|---|---|
| «Πόσο κοστίζει το νέο Renault Clio;» | Greek: from 20900 euros (or 199 a month), engines full hybrid E-Tech 160, TCe 115, Eco-G 120; the dealer confirms |
| «Πού είναι η πλησιέστερη αντιπροσωπεία Dacia στη Θεσσαλονίκη;» | GA Motors (7th km Thessaloniki–N. Moudania) and/or ΒΙΟ-ΚΑΡ PLUS (26ης Οκτωβρίου 70), phone digit by digit, call ahead for hours *(needs PDF 4)* |
| «Τι εγγύηση έχει ένα καινούργιο Dacia;» | 5 years factory warranty as a gift, 6 years anti-corrosion, 5 years roadside assistance |
| «Μου χάλασε το αυτοκίνητο στην εθνική. Τι κάνω;» | Safety first, 112 if in danger; roadside number in the car documents; dealer or customer care 214 444 4640 on weekdays |
| «Ποια ηλεκτρικά έχει η Renault;» | Twingo from 14990, Renault 5 from 22400, Renault 4 from 24400, prices with the ΚΗ3 subsidy and scrappage benefit |
| «Πουλάτε Nissan στην Ελλάδα;» | No: the group sells Nissan elsewhere; in Greece Renault, Dacia, INEOS, and Alpine from 2027 |
| "Where can I see Renault at Auto Athina?" | English: Metropolitan Expo, Hall 3, Stand A1, until 11 October |
| «Θέλω να μιλήσω με κάποιον υπάλληλο» | Transfer not connected in the demo; customer care number, Monday–Friday 9 to 5 |
