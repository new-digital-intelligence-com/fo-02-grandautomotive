"use client";

import { useEffect, useRef } from "react";

type VoiceOrbProps = {
  active: boolean;
  isSpeaking: boolean;
  getInputVolume: () => number;
  getOutputVolume: () => number;
};

/** Pulsing orb driven by the live volume: copper while Katerina speaks, charcoal while she listens. */
export function VoiceOrb({ active, isSpeaking, getInputVolume, getOutputVolume }: VoiceOrbProps) {
  const orbRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const orb = orbRef.current;
    if (!active || !orb) return;
    let frame = 0;
    const tick = () => {
      let volume = 0;
      try {
        volume = isSpeaking ? getOutputVolume() : getInputVolume();
      } catch {
        volume = 0;
      }
      orb.style.transform = `scale(${1 + Math.min(volume, 1) * 0.35})`;
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(frame);
      orb.style.transform = "";
    };
  }, [active, isSpeaking, getInputVolume, getOutputVolume]);

  return (
    <div className="flex h-52 items-center justify-center">
      <div
        ref={orbRef}
        className={`h-36 w-36 rounded-full transition-[background] duration-500 ${
          active
            ? isSpeaking
              ? "bg-[radial-gradient(circle_at_35%_30%,#f3c9a4,#a85a24_55%,#5e2f10)]"
              : "bg-[radial-gradient(circle_at_35%_30%,#ffffff,#8f877d_55%,#1c1b1a)]"
            : "bg-[radial-gradient(circle_at_35%_30%,#ffffff,#ece4d7_60%,#c9bfae)]"
        } shadow-[0_20px_60px_rgba(28,27,26,0.22)]`}
      />
    </div>
  );
}
