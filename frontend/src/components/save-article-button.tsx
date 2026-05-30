"use client";

import { Bookmark, Save } from "lucide-react";
import { useEffect, useState } from "react";

import { bookmarkArticle, getSavedArticles, saveArticle, unsaveArticle } from "@/lib/api";
import type { Article } from "@/types/api";

const STORAGE_KEY = "signcast:saved-articles";

export function SaveArticleButton({ article }: { article: Article }) {
  const [saved, setSaved] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [isBusy, setIsBusy] = useState(false);

  useEffect(() => {
    const existing = readSavedArticles();
    setSaved(existing.some((item) => item.id === article.id));
    setBookmarked(existing.some((item) => item.id === article.id && item.bookmarked));
    getSavedArticles()
      .then((response) => {
        const remote = response.items.find((item) => item.article.id === article.id);
        if (remote) {
          setSaved(true);
          setBookmarked(remote.bookmarked);
        }
      })
      .catch(() => undefined);
  }, [article.id]);

  async function toggle() {
    setIsBusy(true);
    const existing = readSavedArticles();
    const next = saved
      ? existing.filter((item) => item.id !== article.id)
      : [
          {
            id: article.id,
            title: article.title,
            source_name: article.source_name,
            published_at: article.published_at,
            bookmarked
          },
          ...existing.filter((item) => item.id !== article.id)
        ].slice(0, 20);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    setSaved(!saved);
    try {
      if (saved) {
        await unsaveArticle(article.id);
        setBookmarked(false);
      } else {
        await saveArticle(article.id, bookmarked);
      }
    } catch {
      // Local storage fallback keeps the UI usable when the API is offline.
    } finally {
      setIsBusy(false);
    }
  }

  async function toggleBookmark() {
    const next = !bookmarked;
    setBookmarked(next);
    setSaved(true);
    const existing = readSavedArticles();
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify([
        {
          id: article.id,
          title: article.title,
          source_name: article.source_name,
          published_at: article.published_at,
          bookmarked: next
        },
        ...existing.filter((item) => item.id !== article.id)
      ])
    );
    try {
      await bookmarkArticle(article.id, next);
    } catch {
      // Local storage fallback keeps the UI usable when the API is offline.
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={toggle}
        aria-pressed={saved}
        disabled={isBusy}
        className="flex items-center gap-2 rounded border border-ink/15 px-4 py-2 text-sm font-medium transition hover:border-ink/35 disabled:opacity-60"
      >
        <Save size={16} aria-hidden="true" />
        {saved ? "Saved" : "Save"}
      </button>
      <button
        type="button"
        onClick={toggleBookmark}
        aria-pressed={bookmarked}
        className={`flex items-center gap-2 rounded border px-4 py-2 text-sm font-medium transition ${
          bookmarked ? "border-coral bg-coral text-white" : "border-ink/15 hover:border-ink/35"
        }`}
      >
        <Bookmark size={16} aria-hidden="true" />
        {bookmarked ? "Bookmarked" : "Bookmark"}
      </button>
    </div>
  );
}

export interface SavedArticle {
  id: string;
  title: string;
  source_name: string;
  published_at: string;
  bookmarked?: boolean;
}

export function readSavedArticles(): SavedArticle[] {
  if (typeof window === "undefined") {
    return [];
  }
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]") as SavedArticle[];
  } catch {
    return [];
  }
}
