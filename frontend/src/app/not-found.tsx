import Link from "next/link";
import { ArrowLeft, SearchX } from "lucide-react";

export default function NotFound() {
  return (
    <main className="mx-auto grid min-h-[calc(100vh-73px)] max-w-3xl place-items-center px-4 py-8 text-center sm:px-6">
      <section className="rounded border border-ink/10 bg-white p-8 shadow-soft">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded bg-mint/20 text-ink">
          <SearchX size={24} aria-hidden="true" />
        </div>
        <h1 className="mt-4 text-2xl font-semibold">Page not found</h1>
        <p className="mt-3 text-sm leading-6 text-ink/60">
          This SignCast page is not available. Return to the latest accessible headlines.
        </p>
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
