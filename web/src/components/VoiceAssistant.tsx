"use client";

import { ConversationProvider, useConversation } from "@elevenlabs/react";
import { useEffect, useRef, useState } from "react";
import { COPY, type UiLanguage } from "./copy";
import { transcriptText } from "./transcriptText";
import { VoiceOrb } from "./VoiceOrb";

type Line = { id: string; role: "user" | "agent"; text: string };

export function VoiceAssistant() {
  return (
    <ConversationProvider>
      <Assistant />
    </ConversationProvider>
  );
}

function Assistant() {
  const [language, setLanguage] = useState<UiLanguage>("el");
  const [lines, setLines] = useState<Line[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const transcriptEndRef = useRef<HTMLDivElement>(null);
  const t = COPY[language];

  const conversation = useConversation({
    onMessage: ({ message, role }) => {
      const text = transcriptText(message);
      if (text) setLines((current) => [...current, { id: crypto.randomUUID(), role, text }]);
    },
    onConnect: () => setStartedAt(Date.now()),
    onDisconnect: () => setStartedAt(null),
    onError: (message) => {
      console.error(message);
      setError(COPY[language].startError);
    },
  });
  const { status, isSpeaking, isMuted, setMuted } = conversation;
  const connected = status === "connected";
  const connecting = status === "connecting";

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [lines]);

  // Call timer.
  useEffect(() => {
    if (!startedAt) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [startedAt]);

  async function startCall() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch {
      setError(t.micError);
      return;
    }
    const response = await fetch("/api/voice/token", { method: "POST" }).catch(() => null);
    if (!response?.ok) {
      setError(response?.status === 429 ? t.tooManyCalls : t.startError);
      return;
    }
    const { conversationToken } = (await response.json()) as { conversationToken: string };
    setLines([]);
    setNow(Date.now());
    // Greek is Katerina's default; English uses the agent's "en" preset (English greeting, same voice).
    conversation.startSession({
      conversationToken,
      connectionType: "webrtc",
      ...(language === "en" ? { overrides: { agent: { language: "en" } } } : {}),
    });
  }

  function endCall() {
    if (status !== "disconnected") conversation.endSession();
  }

  const statusText = connecting
    ? t.statusConnecting
    : connected
      ? isMuted
        ? t.statusMuted
        : isSpeaking
          ? t.statusSpeaking
          : t.statusListening
      : t.statusIdle;
  const elapsed = startedAt ? Math.max(0, Math.floor((now - startedAt) / 1000)) : 0;
  const clock = `${Math.floor(elapsed / 60)}:${String(elapsed % 60).padStart(2, "0")}`;

  return (
    <div lang={language} className="flex min-h-full flex-1 flex-col">
      <header className="bg-ga-ink text-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="text-lg font-semibold uppercase tracking-[0.18em]">Grand Automotive</span>
            <span className="text-sm text-white/75">{t.brandTagline}</span>
            <span className="rounded-full bg-white/15 px-2.5 py-0.5 text-xs font-medium">{t.demoBadge}</span>
          </div>
          <LanguageSwitch value={language} onChange={setLanguage} disabled={connected || connecting} label={t.languageLabel} />
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-6xl flex-1 gap-6 px-4 py-8 lg:grid-cols-[1fr_1.1fr]">
        <section className="flex flex-col rounded-2xl bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-ga-ink">{t.title}</h1>
          <p className="mt-2 text-ga-muted">{t.subtitle}</p>

          <VoiceOrb
            active={connected}
            isSpeaking={isSpeaking}
            getInputVolume={conversation.getInputVolume}
            getOutputVolume={conversation.getOutputVolume}
          />

          <p className="text-center font-medium text-ga-ink" aria-live="polite">
            {statusText}
            {connected && <span className="ms-2 tabular-nums text-ga-muted">{clock}</span>}
          </p>

          <div className="mt-5 flex flex-wrap justify-center gap-3">
            {connected || connecting ? (
              <>
                <button
                  type="button"
                  onClick={endCall}
                  className="rounded-full bg-ga-red px-7 py-3 font-semibold text-white transition hover:bg-ga-red-dark"
                >
                  {t.end}
                </button>
                <button
                  type="button"
                  onClick={() => setMuted(!isMuted)}
                  disabled={!connected}
                  aria-pressed={isMuted}
                  className="rounded-full border border-ga-line px-6 py-3 font-semibold text-ga-ink transition hover:bg-ga-mist disabled:opacity-50"
                >
                  {isMuted ? t.unmute : t.mute}
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={() => void startCall()}
                className="rounded-full bg-ga-copper px-8 py-3 text-lg font-semibold text-white shadow-md transition hover:bg-ga-copper-dark"
              >
                {t.start}
              </button>
            )}
          </div>
          {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-center text-sm text-ga-red-dark">{error}</p>}
          <p className="mt-4 text-center text-xs text-ga-muted">{t.callLimit}</p>
        </section>

        <section className="flex min-h-80 flex-col rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-ga-ink">{t.transcriptTitle}</h2>
          <div className="mt-4 max-h-[28rem] flex-1 space-y-3 overflow-y-auto pe-1">
            {lines.length === 0 ? (
              <p className="text-sm text-ga-muted">{t.transcriptEmpty}</p>
            ) : (
              lines.map((line) => (
                <div key={line.id} className={`flex ${line.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                      line.role === "user" ? "bg-ga-mist text-ga-text" : "bg-ga-ink text-white"
                    }`}
                  >
                    <p className="text-xs font-semibold opacity-70">{line.role === "user" ? t.you : t.agent}</p>
                    <p className="mt-0.5 whitespace-pre-wrap leading-relaxed">{line.text}</p>
                  </div>
                </div>
              ))
            )}
            <div ref={transcriptEndRef} />
          </div>
        </section>

        <section className="rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-ga-ink">{t.tryTitle}</h2>
          <ul className="mt-3 flex flex-wrap gap-2">
            {t.tryQuestions.map((question) => (
              <li key={question} className="rounded-full bg-ga-mist px-3.5 py-1.5 text-sm text-ga-text">
                {question}
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-ga-ink">{t.helpTitle}</h2>
          <ul className="mt-3 space-y-1.5 text-ga-text">
            {t.help.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="text-ga-copper" aria-hidden>
                  ●
                </span>
                {item}
              </li>
            ))}
          </ul>
          <h3 className="mt-5 font-bold text-ga-ink">{t.brandsTitle}</h3>
          <p className="mt-1 text-sm text-ga-muted">{t.brands}</p>
        </section>
      </main>

      <footer className="px-4 pb-6 text-center text-xs text-ga-muted">{t.footer}</footer>
    </div>
  );
}

function LanguageSwitch({
  value,
  onChange,
  disabled,
  label,
}: {
  value: UiLanguage;
  onChange: (language: UiLanguage) => void;
  disabled: boolean;
  label: string;
}) {
  const options: { value: UiLanguage; label: string }[] = [
    { value: "el", label: "Ελληνικά" },
    { value: "en", label: "English" },
  ];
  return (
    <div className="flex rounded-full bg-white/15 p-1" role="group" aria-label={label}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          disabled={disabled}
          aria-pressed={value === option.value}
          className={`rounded-full px-3.5 py-1 text-sm font-medium transition disabled:cursor-not-allowed ${
            value === option.value ? "bg-white text-ga-ink" : "text-white/85 hover:text-white"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
