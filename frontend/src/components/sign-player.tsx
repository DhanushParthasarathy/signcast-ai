"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Play, SkipBack, SkipForward, XCircle } from "lucide-react";
import { useMemo, useState } from "react";

import type { SignSequenceItem } from "@/types/api";

export function SignPlayer({ sequence }: { sequence: SignSequenceItem[] }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const active = sequence[activeIndex];
  const readyCount = useMemo(() => sequence.filter((item) => item.status === "ready").length, [sequence]);

  function next() {
    setActiveIndex((index) => (index + 1) % Math.max(sequence.length, 1));
  }

  function previous() {
    setActiveIndex((index) => (index - 1 + sequence.length) % Math.max(sequence.length, 1));
  }

  if (!sequence.length) {
    return (
      <div className="rounded border border-dashed border-ink/20 bg-white p-6 text-sm text-ink/60">
        No sign sequence has been generated for this article.
      </div>
    );
  }

  return (
    <section className="rounded border border-ink/10 bg-white p-5 shadow-soft" aria-label="Sign animation player">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Sign Animation Player</h2>
          <p className="text-sm text-ink/60">
            {readyCount} of {sequence.length} clips ready
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={previous}
            title="Previous sign"
            className="flex h-10 w-10 items-center justify-center rounded border border-ink/15 text-ink transition hover:border-ink/35"
          >
            <SkipBack size={18} aria-hidden="true" />
          </button>
          <button
            type="button"
            onClick={next}
            title="Next sign"
            className="flex h-10 w-10 items-center justify-center rounded bg-ink text-canvas transition hover:bg-ink/90"
          >
            <SkipForward size={18} aria-hidden="true" />
          </button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_240px]">
        <div className="flex aspect-video items-center justify-center rounded bg-ink text-canvas" aria-live="polite">
          {active?.clip_url ? (
            <video
              key={active.clip_url}
              src={active.clip_url}
              controls
              aria-label={`Sign clip for ${active.token}`}
              className="h-full w-full rounded object-cover"
            />
          ) : (
            <motion.div
              initial={{ scale: 0.92, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex flex-col items-center gap-3 text-center"
            >
              <Play size={34} aria-hidden="true" />
              <span className="text-2xl font-semibold">{active?.token}</span>
              <span className="text-sm text-canvas/70">Dictionary clip needed</span>
            </motion.div>
          )}
        </div>
        <div className="grid max-h-72 gap-2 overflow-auto pr-1">
          {sequence.map((item, index) => (
            <button
              key={`${item.token}-${index}`}
              type="button"
              onClick={() => setActiveIndex(index)}
              className={`flex items-center justify-between rounded border px-3 py-2 text-left text-sm ${
                activeIndex === index
                  ? "border-ink bg-ink text-canvas"
                  : "border-ink/10 bg-canvas text-ink"
              }`}
            >
              <span>{item.token}</span>
              <span className="flex items-center gap-1 text-xs opacity-75">
                {item.status === "ready" ? (
                  <CheckCircle2 size={13} aria-hidden="true" />
                ) : (
                  <XCircle size={13} aria-hidden="true" />
                )}
                {item.status}
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
