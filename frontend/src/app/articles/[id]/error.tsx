"use client";

import Link from "next/link";
import { AlertTriangle, ArrowLeft } from "lucide-react";

export default function ArticleError({ error }: { error: Error; reset: () => void }) {
  return (
    <main className="mx-auto grid min-h-[calc(100vh-73px)] max-w-3xl place-items-center px-4 py-8 text-center sm:px-6">
      <section className="rounded border border-ink/10 bg-white p-8 shadow-soft">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded bg-coral/15 text-coral">
          <AlertTriangle size={24} aria-hidden="true" />
        </div>
        <h1 className="mt-4 text-2xl font-semibold">Article unavailable</h1>
        <p className="mt-3 text-sm leading-6 text-ink/60">{error.message}</p>
        <Link
          href="/"
          className="mx-auto mt-5 flex w-fit items-center gap-2 rounded bg-ink px-4 py-2 text-sm font-medium text-canvas"
        >
          <ArrowLeft size={16} aria-hidden="true" />
          Back to News
        </Link>
      </section>
    </main>
  );
}
