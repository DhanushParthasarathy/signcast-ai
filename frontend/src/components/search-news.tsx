"use client";

import { Search } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

export function SearchNews() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (query.trim()) {
      params.set("q", query.trim());
    } else {
      params.delete("q");
    }
    router.push(`/?${params.toString()}`);
  }

  return (
    <form onSubmit={submit} className="flex w-full max-w-xl items-center gap-2">
      <label className="sr-only" htmlFor="news-search">
        Search news
      </label>
      <input
        id="news-search"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search accessible news"
        className="min-h-11 flex-1 rounded border border-ink/15 bg-white px-3 text-sm outline-none transition focus:border-ink"
      />
      <button
        type="submit"
        title="Search"
        className="flex h-11 w-11 items-center justify-center rounded bg-coral text-white transition hover:bg-coral/90"
      >
        <Search size={18} aria-hidden="true" />
      </button>
    </form>
  );
}
