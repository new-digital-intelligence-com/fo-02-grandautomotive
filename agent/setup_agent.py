"""Creates (first run) or updates (later runs) the Grand Automotive Greek voice agent on ElevenLabs.

- Adds the official Renault, Dacia and Grand Automotive web pages to the knowledge base, with auto-sync every 7 days.
- Creates the agent "Katerina" with the prompt in prompt.md: Greek by default, an English preset, the Eleven v4 Turbo voice model
  and a native Greek voice.
- Attaches the knowledge-base PDFs synced from Google Drive (found by name in the workspace library: 01_GA_… to 06_GA_…), and
  keeps anything else added to the agent in the dashboard. Run it again after the PDFs are uploaded.
- The website has no login, so the agent only accepts calls started with a token from the website (enable_auth), and has a
  daily limit and a limit of calls at the same time (CALL_LIMITS).

Settings come from the website's own ../web/.env.local (ELEVENLABS_API_KEY); environment variables win.

Usage: python setup_agent.py   (on Windows, prefix with PYTHONIOENCODING=utf-8: the output has Greek letters)
IDs are saved in agent_ids.json (no secrets in it). Creating or updating an agent does not use conversation credits.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IDS_FILE = os.path.join(HERE, "agent_ids.json")
WEB_ENV = os.path.join(HERE, "..", "web", ".env.local")
API = "https://api.elevenlabs.io"


def load_settings() -> dict[str, str]:
    settings: dict[str, str] = {}
    if os.path.exists(WEB_ENV):
        for line in open(WEB_ENV, encoding="utf-8"):
            name, sep, value = line.strip().partition("=")
            if sep and not name.startswith("#"):
                settings[name] = value.strip().strip('"')
    return {**settings, **{k: v for k, v in os.environ.items() if k.startswith("ELEVENLABS_")}}


SETTINGS = load_settings()
KEY = SETTINGS.get("ELEVENLABS_API_KEY") or sys.exit("ELEVENLABS_API_KEY is not set (../web/.env.local)")

NAME = "Grand Automotive Greece – Voice Assistant (Demo)"
# Eleven v4 Turbo: ElevenLabs' fast, expressive model for agents (90+ languages, Greek included), for Greek and English.
TTS_MODEL = "eleven_v4_turbo"
EN_TTS_MODEL = "eleven_v4_turbo"
LLM = "gemini-3.7-flash"  # the LLM the Budget Arabia agent uses (tested by the user there)
EMBEDDING_MODEL = "multilingual_e5_large_instruct"  # RAG search in Greek and English
# Starts with a "k" sound on purpose: ElevenLabs' generated audio of the old greeting («Γεια σας, …») always began mid-sound,
# so callers heard half of «Γεια» (client remark, confirmed in ElevenLabs' own call recordings, 9 Oct 2026). A word that
# starts with a plosive (k, p, t) begins sharply anyway, so a hard start cannot be heard.
FIRST_MESSAGE_EL = "Καλώς ήρθατε στην Grand Automotive! Είμαι η Κατερίνα. Πώς μπορώ να σας βοηθήσω σήμερα;"
FIRST_MESSAGE_EN = "Hello, this is Katerina from Grand Automotive, the Renault and Dacia importer in Greece. How can I help you today?"

# "Katerina – Confident and poised": a native Greek female voice from ElevenLabs' own library, verified for Greek (el-GR) on
# Eleven v4 Turbo. (voice_id, library owner id, voice library name). Other native Greek voices verified for v4 Turbo:
# Yiannis – Friendly and warm (2KCRgZhHPaecTJfl6gAl, male), Dimitris – Deep and powerful (oM0rTT4KZZcrSuEN0UnQ, male),
# Nikos – Deep and resonant (QnPbsq4pmOZkrE4RQQCA, older male); same owner id.
VOICE = ("t7C9cEkpMwHG1IMZlJJ5", "64cbc624eb5aab4e95a968e1f41d75402277cca6e549036ed17e56ea33bbbc9e", "Katerina – Confident and poised")

# Brand and model names the speech recognition should expect in Greek speech.
ASR_KEYWORDS = ["Grand Automotive", "GA Hellas", "GA Motors", "Renault", "Dacia", "INEOS", "Grenadier", "Alpine", "Clio",
                "Captur", "Symbioz", "Austral", "Arkana", "Rafale", "Twingo", "Sandero", "Stepway", "Jogger", "Duster",
                "Bigster", "Spring", "Striker", "Kangoo", "Trafic", "Master", "E-Tech", "Eco-G", "tribrid", "Auto Athina"]

# The website has no login: only calls started with a token from the website are accepted (enable_auth), at most
# 4 at the same time and 50 a day. Each call lasts at most 10 minutes (MAX_CALL_SECONDS).
CALL_LIMITS = {"agent_concurrency_limit": 4, "daily_limit": 50, "bursting_enabled": False}
MAX_CALL_SECONDS = 600

# Official pages whose text is in the HTML. auto_remove: drop the document when the page disappears (offers, the motor show).
# Not here on purpose (agent_ids.json "retired_documents"): renault.gr/contact.html and grandautomotive.eu/where-we-operate,
# whose copies in ElevenLabs miss the phone number and e-mail, or drop brands from the list; the PDFs have both.
URLS = [
    ("Renault Ελλάδα – Γκάμα και τιμές", "https://www.renault.gr/range.html", False),
    ("Dacia Ελλάδα – Γκάμα και τιμές", "https://www.dacia.gr/vehicles.html", False),
    ("Dacia Your Way – προσφορά", "https://www.dacia.gr/dacia-your-way.html", True),
    ("Renault – After Sales και εγγύηση", "https://www.renault.gr/services/services.html", False),
    ("Dacia – Εγγύηση", "https://www.dacia.gr/services/warranty.html", False),
    ("rnlt© Athens – concept store Renault", "https://www.renault.gr/rnlt-athens.html", False),
    ("Renault στην Auto Athina 2026", "https://www.renault.gr/renault-in-auto-athina-2026.html", True),
    ("Dacia στην Auto Athina 2026", "https://www.dacia.gr/dacia-in-auto-athina-2026.html", True),
]


def call(method: str, path: str, body: dict | None = None) -> dict:
    request = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"xi-api-key": KEY, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        sys.exit(f"{method} {path} -> {error.code}: {error.read().decode(errors='replace')[:1500]}")


def load_ids() -> dict:
    return json.load(open(IDS_FILE, encoding="utf-8")) if os.path.exists(IDS_FILE) else {"url_documents": {}}


def save_ids(ids: dict) -> None:
    with open(IDS_FILE, "w", encoding="utf-8") as file:
        json.dump(ids, file, ensure_ascii=False, indent=2)


def url_documents(ids: dict) -> list[dict]:
    locators = []
    for name, url, auto_remove in URLS:
        doc_id = ids["url_documents"].get(url)
        if not doc_id:
            created = call("POST", "/v1/convai/knowledge-base/url", {
                "url": url, "name": name, "enable_auto_sync": True, "auto_remove": auto_remove, "minimum_frequency_days": 7,
            })
            doc_id = created["id"]
            ids["url_documents"][url] = doc_id
            save_ids(ids)
            print("added web page:", name, doc_id)
        locators.append({"type": "url", "name": name, "id": doc_id, "usage_mode": "auto"})
    return locators


def ensure_voice() -> None:
    """A voice from the public library must be in the account before an agent can use it."""
    mine = {v["voice_id"] for v in call("GET", "/v1/voices").get("voices", [])}
    voice_id, owner_id, name = VOICE
    if voice_id not in mine:
        call("POST", f"/v1/voices/add/{owner_id}/{voice_id}", {"new_name": f"Grand Automotive – {name}"})
        print("added voice:", name)


def library_pdfs() -> list[dict]:
    """The knowledge-base PDFs synced from Google Drive (01_GA_… to 06_GA_…), found by name in the workspace library."""
    documents, cursor = [], None
    while True:  # the search parameter only matches the start of a name, so read the whole library
        page = call("GET", "/v1/convai/knowledge-base?page_size=100" + (f"&cursor={urllib.parse.quote(cursor)}" if cursor else ""))
        documents += page.get("documents", [])
        cursor = page.get("next_cursor")
        if not page.get("has_more") or not cursor:
            break
    newest: dict[str, dict] = {}
    for doc in documents:
        name = doc.get("name") or ""
        if re.fullmatch(r"0\d_GA_.+\.pdf", name):
            created = (doc.get("metadata") or {}).get("created_at_unix_secs", 0)
            if name not in newest or created > newest[name]["created"]:
                newest[name] = {"id": doc["id"], "created": created}
    return [{"type": "file", "name": name, "id": d["id"], "usage_mode": "auto"} for name, d in sorted(newest.items())]


def rag_indexes(documents: list[dict]) -> None:
    """RAG only searches documents that have an index for the agent's embedding model: create the missing ones (the dashboard
    does this by itself; the API does not). Indexing finishes in the background."""
    result = call("POST", "/v1/convai/knowledge-base/rag-index", {"items": [
        {"document_id": d["id"], "create_if_missing": True, "model": EMBEDDING_MODEL} for d in documents]})
    # {document_id: {"status": "success", "data": {"status": "new" | "processing" | "succeeded" | ...}}}
    statuses = [(item.get("data") or {}).get("status") or item.get("status") for item in result.values()]
    print("rag indexes:", {status: statuses.count(status) for status in set(statuses)})


def conversation_config(knowledge_base: list[dict]) -> dict:
    prompt = open(os.path.join(HERE, "prompt.md"), encoding="utf-8").read()
    return {
        "agent": {
            "first_message": FIRST_MESSAGE_EL,
            "language": "el",
            "prompt": {
                "prompt": prompt,
                "llm": LLM,
                "temperature": 0.2,
                "timezone": "Europe/Athens",
                "ignore_default_personality": True,
                "knowledge_base": knowledge_base,
                "tool_ids": [],
                "rag": {"enabled": True, "embedding_model": EMBEDDING_MODEL, "max_vector_distance": 0.6,
                        "max_documents_length": 50000, "max_retrieved_rag_chunks_count": 20},
                "built_in_tools": {
                    "end_call": {"type": "system", "name": "end_call", "description": "", "params": {"system_tool_type": "end_call"}},
                    "language_detection": {"type": "system", "name": "language_detection", "description": "",
                                           "params": {"system_tool_type": "language_detection", "only_at_conversation_start": False}},
                },
            },
        },
        "tts": {"model_id": TTS_MODEL, "voice_id": VOICE[0], "stability": 0.5, "similarity_boost": 0.8, "speed": 1.0,
                # audio tags are for the v3 models only (ElevenLabs switches them off for other models anyway)
                "expressive_mode": False,
                # Numbers are normalised for speech by ElevenLabs after the LLM, so Katerina writes digits and the transcript
                # shows 2144444640, not number words ("system_prompt", the default, makes the LLM write words).
                "text_normalisation_type": "elevenlabs",
                "agent_output_audio_format": "pcm_24000"},
        "asr": {"quality": "high", "provider": "scribe_realtime", "user_input_audio_format": "pcm_16000", "keywords": ASR_KEYWORDS},
        "turn": {"turn_timeout": 7, "mode": "turn", "turn_eagerness": "normal"},
        "conversation": {"max_duration_seconds": MAX_CALL_SECONDS},
        "language_presets": {
            "en": {"overrides": {"agent": {"first_message": FIRST_MESSAGE_EN, "language": "en"}, "tts": {"model_id": EN_TTS_MODEL}}},
        },
    }


PLATFORM_SETTINGS = {
    # the website may pass the caller's language and first message; nothing else can be changed from outside
    "overrides": {"conversation_config_override": {"agent": {"first_message": True, "language": True}}},
    # only conversations started with a one-use token from the website's server (the API key stays there)
    "auth": {"enable_auth": True},
    "call_limits": CALL_LIMITS,
}


def main() -> None:
    ids = load_ids()
    if ids.get("agent_id") and "--force" not in sys.argv:
        # Someone may be editing the agent in the dashboard: never overwrite an unpublished draft.
        branches = call("GET", f"/v1/convai/agents/{ids['agent_id']}/branches").get("results", [])
        if any(branch.get("draft_exists") for branch in branches):
            sys.exit("The agent has an unpublished draft in the dashboard: publish or discard it first (or run with --force).")
    ensure_voice()
    pdfs = library_pdfs()
    documents = url_documents(ids) + pdfs
    print("knowledge documents:", ", ".join(d["name"] for d in documents))
    if not pdfs:
        print("no 0N_GA_*.pdf in the knowledge base yet: upload them (Google Drive), then run this again")
    rag_indexes(documents)
    if not ids.get("agent_id"):
        created = call("POST", "/v1/convai/agents/create", {
            "name": NAME, "tags": ["grand-automotive", "greek", "demo", "ndi"],
            "conversation_config": conversation_config(documents), "platform_settings": PLATFORM_SETTINGS,
        })
        ids["agent_id"] = created["agent_id"]
        save_ids(ids)
        print("created agent:", ids["agent_id"])
    else:
        current = call("GET", f"/v1/convai/agents/{ids['agent_id']}")
        ours = {d["id"] for d in documents} | {d["name"] for d in documents}
        retired = ids.get("retired_documents", {})
        kept = [d for d in current["conversation_config"]["agent"]["prompt"].get("knowledge_base", [])
                if d["id"] not in ours and d["name"] not in ours  # drops an older copy of one of our PDFs
                and d["id"] not in retired]
        call("PATCH", f"/v1/convai/agents/{ids['agent_id']}", {
            "name": NAME, "conversation_config": conversation_config(documents + kept), "platform_settings": PLATFORM_SETTINGS,
        })
        print("updated agent:", ids["agent_id"], f"(kept {len(kept)} other knowledge documents)")

    agent = call("GET", f"/v1/convai/agents/{ids['agent_id']}")
    config, platform = agent["conversation_config"], agent.get("platform_settings") or {}
    print("check -> language:", config["agent"]["language"], "| voice:", config["tts"]["voice_id"], "| tts:", config["tts"]["model_id"],
          "| en preset tts:", ((config.get("language_presets") or {}).get("en") or {}).get("overrides", {}).get("tts", {}).get("model_id"),
          "| llm:", config["agent"]["prompt"]["llm"], "| knowledge docs:", len(config["agent"]["prompt"]["knowledge_base"]),
          "| rag:", config["agent"]["prompt"]["rag"]["enabled"],
          "| tools:", [k for k, v in (config["agent"]["prompt"].get("built_in_tools") or {}).items() if v],
          "| auth:", (platform.get("auth") or {}).get("enable_auth"), "| call limits:", platform.get("call_limits"),
          "| max call:", config["conversation"]["max_duration_seconds"], "s")


if __name__ == "__main__":
    main()
