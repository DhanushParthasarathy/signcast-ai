"use client";

import Link from "next/link";
import { Bookmark, Clock, Heart, Languages, PlayCircle } from "lucide-react";
import { useEffect, useState } from "react";

import { MetricCard } from "@/components/metric-card";
import { readSavedArticles, type SavedArticle } from "@/components/save-article-button";
import { getPreferences, getRecentlyViewed, getSavedArticles, updatePreferences } from "@/lib/api";
import { formatDate } from "@/lib/format";
import type { NewsCategory, UserPreferences, WatchHistoryItem } from "@/types/api";

const categories: NewsCategory[] = ["general", "business", "health", "science", "technology"];

export function DashboardClient() {
  const [saved, setSaved] = useState<SavedArticle[]>([]);
  const [bookmarks, setBookmarks] = useState<SavedArticle[]>([]);
  const [recent, setRecent] = useState<WatchHistoryItem[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences>({
    favorite_categories: [],
    preferred_language: "en",
    captions_enabled: true,
    playback_speed: 1
  });

  useEffect(() => {
    const localSaved = readSavedArticles();
    setSaved(localSaved);
    setBookmarks(localSaved.filter((item) => item.bookmarked));

    getSavedArticles()
      .then((response) => {
        const mapped = response.items.map((item) => ({
          id: item.article.id,
          title: item.article.title,
          source_name: item.article.source_name,
          published_at: item.article.published_at,
          bookmarked: item.bookmarked
        }));
        setSaved(mapped);
        setBookmarks(mapped.filter((item) => item.bookmarked));
      })
      .catch(() => undefined);

    getRecentlyViewed()
      .then((response) => setRecent(response.items))
      .catch(() => undefined);

    getPreferences()
      .then(setPreferences)
      .catch(() => undefined);
  }, []);

  async function toggleCategory(category: NewsCategory) {
    const exists = preferences.favorite_categories.includes(category);
    const favorite_categories = exists
      ? preferences.favorite_categories.filter((item) => item !== category)
      : [...preferences.favorite_categories, category];
    const next = { ...preferences, favorite_categories };
    setPreferences(next);
    try {
      setPreferences(await updatePreferences({ favorite_categories }));
    } catch {
      setPreferences(next);
    }
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-7 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-normal text-coral">Your workspace</p>
          <h1 className="mt-2 text-3xl font-semibold">Dashboard</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-ink/60">
            Track saved articles, bookmarks, watch history, and accessibility preferences.
          </p>
        </div>
        <Link href="/" className="rounded bg-ink px-4 py-2 text-sm font-medium text-canvas">
          Browse News
        </Link>
      </div>

      <section className="grid gap-4 md:grid-cols-3">
        <MetricCard icon={Heart} label="Saved articles" value={String(saved.length)} tone="coral" />
        <MetricCard icon={Bookmark} label="Bookmarks" value={String(bookmarks.length)} tone="mint" />
        <MetricCard icon={PlayCircle} label="Recently viewed" value={String(recent.length)} tone="berry" />
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-[1fr_420px]">
        <div className="rounded border border-ink/10 bg-white shadow-soft">
          <div className="border-b border-ink/10 p-5">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <Heart size={18} aria-hidden="true" />
              Saved News
            </h2>
          </div>
          <div className="divide-y divide-ink/10">
            {saved.length ? (
              saved.map((article) => (
                <Link
                  key={article.id}
                  href={`/articles/${article.id}`}
                  className="block p-5 transition hover:bg-canvas"
                >
                  <p className="font-medium leading-6">{article.title}</p>
                  <p className="mt-1 text-sm text-ink/55">
                    {article.source_name} - {formatDate(article.published_at)}
                  </p>
                </Link>
              ))
            ) : (
              <div className="p-5 text-sm leading-6 text-ink/60">
                Saved articles will appear here after you press Save on an article page.
              </div>
            )}
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white shadow-soft">
          <div className="border-b border-ink/10 p-5">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <Clock size={18} aria-hidden="true" />
              Recently Viewed
            </h2>
          </div>
          <div className="divide-y divide-ink/10">
            {recent.length ? (
              recent.map((item) => (
                <Link key={item.id} href={`/articles/${item.article.id}`} className="block p-5 transition hover:bg-canvas">
                  <div className="flex items-start justify-between gap-4">
                    <p className="font-medium leading-6">{item.article.title}</p>
                    <span className="rounded bg-mint/20 px-2 py-1 text-xs font-medium">
                      {item.completed ? "Complete" : "Viewed"}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-ink/55">
                    {item.duration_seconds}s - {formatDate(item.watched_at)}
                  </p>
                </Link>
              ))
            ) : (
              <div className="p-5 text-sm leading-6 text-ink/60">
                Recently viewed articles will appear after you open an article.
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="mt-6 rounded border border-ink/10 bg-white p-5 shadow-soft">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Languages size={18} aria-hidden="true" />
          Favorite Categories
        </h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {categories.map((category) => {
            const active = preferences.favorite_categories.includes(category);
            return (
              <button
                key={category}
                type="button"
                onClick={() => toggleCategory(category)}
                className={`rounded border px-3 py-2 text-sm capitalize ${
                  active ? "border-ink bg-ink text-canvas" : "border-ink/15 hover:border-ink/35"
                }`}
              >
                {category}
              </button>
            );
          })}
        </div>
      </section>
    </main>
  );
}
