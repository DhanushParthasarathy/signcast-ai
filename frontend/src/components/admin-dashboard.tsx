"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { AlertTriangle, BarChart3, CheckCircle2, Search, Trash2, Upload, Video } from "lucide-react";

import {
  deleteSignEntry,
  getAdminBugReports,
  getAdminAnalytics,
  getAdminFeedback,
  getAdminRatings,
  getGenerationFailures,
  getMissingGlosses,
  getAdminToken,
  getSignDictionary,
  setAdminToken,
  uploadSignClip
} from "@/lib/api";
import { formatDate } from "@/lib/format";
import type {
  AdminAnalytics,
  BugReportItem,
  FeedbackItem,
  GenerationFailure,
  MissingGloss,
  SignDictionaryEntry,
  TranslationRatingItem
} from "@/types/api";

const emptyAnalytics: AdminAnalytics = {
  metrics: [],
  category_usage: [],
  most_viewed: [],
  search_topics: [],
  engagement: [],
  recent_failures: []
};

export function AdminDashboard() {
  const [dictionary, setDictionary] = useState<SignDictionaryEntry[]>([]);
  const [analytics, setAnalytics] = useState<AdminAnalytics>(emptyAnalytics);
  const [missing, setMissing] = useState<MissingGloss[]>([]);
  const [failures, setFailures] = useState<GenerationFailure[]>([]);
  const [feedback, setFeedback] = useState<FeedbackItem[]>([]);
  const [ratings, setRatings] = useState<TranslationRatingItem[]>([]);
  const [bugReports, setBugReports] = useState<BugReportItem[]>([]);
  const [adminToken, setAdminTokenState] = useState("");
  const [query, setQuery] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const maxCategoryViews = useMemo(
    () => Math.max(...analytics.category_usage.map((item) => item.views), 1),
    [analytics.category_usage]
  );

  useEffect(() => {
    setAdminTokenState(getAdminToken());
    void refresh();
  }, []);

  async function refresh() {
    try {
      const [
        dictionaryResponse,
        analyticsResponse,
        missingResponse,
        failuresResponse,
        feedbackResponse,
        ratingsResponse,
        bugReportsResponse
      ] = await Promise.all([
        getSignDictionary(query),
        getAdminAnalytics(),
        getMissingGlosses(),
        getGenerationFailures(),
        getAdminFeedback(),
        getAdminRatings(),
        getAdminBugReports()
      ]);
      setDictionary(dictionaryResponse.entries);
      setAnalytics(analyticsResponse);
      setMissing(missingResponse.items);
      setFailures(failuresResponse);
      setFeedback(feedbackResponse);
      setRatings(ratingsResponse);
      setBugReports(bugReportsResponse);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unable to load admin data");
    }
  }

  function saveAdminToken(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAdminToken(adminToken);
    setMessage("Admin token saved in this browser.");
    void refresh();
  }

  async function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await getSignDictionary(query);
    setDictionary(response.entries);
  }

  async function upload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const raw = new FormData(form);
    const formData = new FormData();
    formData.set("gloss", String(raw.get("gloss") ?? ""));
    const video = raw.get("video");
    if (video instanceof File && video.size > 0) {
      formData.set("video", video);
    }
    const videoUrl = String(raw.get("video_url") ?? "").trim();
    if (videoUrl) {
      formData.set("video_url", videoUrl);
    }
    const thumbnailUrl = String(raw.get("thumbnail_url") ?? "").trim();
    if (thumbnailUrl) {
      formData.set("thumbnail_url", thumbnailUrl);
    }
    setMessage(null);
    try {
      await uploadSignClip(formData);
      form.reset();
      setMessage("Clip uploaded and queued for review.");
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Upload failed");
    }
  }

  async function remove(id: string) {
    await deleteSignEntry(id);
    setDictionary((items) => items.filter((item) => item.id !== id));
  }

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-normal text-coral">Operations</p>
        <h1 className="mt-2 text-3xl font-semibold">Admin Dashboard</h1>
        <p className="mt-2 text-sm text-ink/60">
          Upload sign clips, manage dictionary coverage, review failures, and monitor usage.
        </p>
      </div>

      <form onSubmit={saveAdminToken} className="mb-6 flex flex-col gap-3 rounded border border-ink/10 bg-white p-4 shadow-soft sm:flex-row sm:items-end">
        <label className="grid flex-1 gap-2 text-sm font-medium">
          Admin API token
          <input
            value={adminToken}
            onChange={(event) => setAdminTokenState(event.target.value)}
            type="password"
            className="rounded border border-ink/15 px-3 py-2"
            placeholder="Paste production admin token"
          />
        </label>
        <button className="rounded bg-ink px-4 py-2 font-medium text-canvas">Save Token</button>
      </form>

      <section className="grid gap-4 md:grid-cols-5">
        {analytics.metrics.map((metric) => (
          <div key={metric.label} className="rounded border border-ink/10 bg-white p-4 shadow-soft">
            <p className="text-2xl font-semibold">{metric.value}</p>
            <p className="mt-1 text-sm text-ink/60">{metric.label}</p>
          </div>
        ))}
      </section>

      <div className="mt-6 grid gap-6 lg:grid-cols-[380px_1fr]">
        <section className="rounded border border-ink/10 bg-white p-5 shadow-soft">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <Upload size={18} aria-hidden="true" />
            Upload Sign Clip
          </h2>
          <form onSubmit={upload} className="mt-5 grid gap-4">
            <label className="grid gap-2 text-sm font-medium">
              Gloss
              <input name="gloss" required className="rounded border border-ink/15 px-3 py-2" placeholder="SATELLITE" />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Video file
              <input name="video" type="file" accept="video/mp4,video/webm,video/quicktime" className="text-sm" />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Video URL
              <input name="video_url" className="rounded border border-ink/15 px-3 py-2" placeholder="https://..." />
            </label>
            <label className="grid gap-2 text-sm font-medium">
              Thumbnail URL
              <input name="thumbnail_url" className="rounded border border-ink/15 px-3 py-2" placeholder="Optional" />
            </label>
            <button className="flex items-center justify-center gap-2 rounded bg-coral px-4 py-2 font-medium text-white">
              <Upload size={17} aria-hidden="true" />
              Upload
            </button>
            {message ? <p className="rounded bg-canvas p-3 text-sm text-ink/70">{message}</p> : null}
          </form>
        </section>

        <section className="overflow-hidden rounded border border-ink/10 bg-white shadow-soft">
          <div className="flex flex-col gap-4 border-b border-ink/10 p-5 md:flex-row md:items-center md:justify-between">
            <h2 className="flex items-center gap-2 text-lg font-semibold">
              <Video size={18} aria-hidden="true" />
              Dictionary
            </h2>
            <form onSubmit={search} className="flex gap-2">
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="rounded border border-ink/15 px-3 py-2 text-sm"
                placeholder="Search gloss"
              />
              <button title="Search" className="flex h-10 w-10 items-center justify-center rounded bg-ink text-canvas">
                <Search size={16} aria-hidden="true" />
              </button>
            </form>
          </div>
          <div className="divide-y divide-ink/10">
            {dictionary.map((entry) => (
              <div key={entry.id} className="grid gap-3 p-5 md:grid-cols-[80px_1fr_220px_44px] md:items-center">
                <div className="flex h-14 w-20 items-center justify-center overflow-hidden rounded bg-ink text-canvas">
                  {entry.thumbnail_url ? <img src={entry.thumbnail_url} alt="" className="h-full w-full object-cover" /> : <Video size={18} />}
                </div>
                <div>
                  <p className="font-mono text-sm font-semibold">{entry.gloss}</p>
                  <p className="mt-1 truncate text-sm text-ink/55">{entry.video_url}</p>
                </div>
                <span className="flex items-center gap-2 text-sm text-ink/60">
                  <CheckCircle2 size={16} aria-hidden="true" />
                  Uploaded {formatDate(entry.created_at)}
                </span>
                <button
                  type="button"
                  title="Delete"
                  onClick={() => remove(entry.id)}
                  className="flex h-10 w-10 items-center justify-center rounded border border-ink/15 text-coral"
                >
                  <Trash2 size={16} aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="rounded border border-ink/10 bg-white p-5 shadow-soft">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <BarChart3 size={18} aria-hidden="true" />
            Usage By Category
          </h2>
          <div className="mt-5 grid gap-3">
            {analytics.category_usage.length ? analytics.category_usage.map((item) => (
              <div key={item.category}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="capitalize">{item.category}</span>
                  <span>{item.views}</span>
                </div>
                <div className="h-2 rounded bg-canvas">
                  <div className="h-2 rounded bg-mint" style={{ width: `${(item.views / maxCategoryViews) * 100}%` }} />
                </div>
              </div>
            )) : <p className="text-sm text-ink/60">No usage data yet.</p>}
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white p-5 shadow-soft">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <AlertTriangle size={18} aria-hidden="true" />
            Missing Glosses
          </h2>
          <div className="mt-4 grid gap-2">
            {missing.length ? missing.map((item) => (
              <div key={item.gloss} className="flex justify-between rounded bg-canvas px-3 py-2 text-sm">
                <span className="font-mono">{item.gloss}</span>
                <span>{item.occurrences}</span>
              </div>
            )) : <p className="text-sm text-ink/60">No missing glosses reported.</p>}
          </div>
        </div>

        <div className="rounded border border-ink/10 bg-white p-5 shadow-soft">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <AlertTriangle size={18} aria-hidden="true" />
            Generation Failures
          </h2>
          <div className="mt-4 grid gap-3">
            {failures.length ? failures.map((failure) => (
              <div key={failure.id} className="rounded border border-ink/10 p-3">
                <p className="font-mono text-xs">{failure.gloss_tokens.join(" ")}</p>
                <p className="mt-2 text-xs text-coral">{failure.error_message}</p>
                <p className="mt-2 text-xs text-ink/50">{failure.attempts} attempts</p>
              </div>
            )) : <p className="text-sm text-ink/60">No generation failures.</p>}
          </div>
        </div>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-3">
        <ReviewPanel title="User Feedback" empty="No feedback yet.">
          {feedback.map((item) => (
            <div key={item.id} className="rounded border border-ink/10 p-3 text-sm">
              <div className="flex justify-between gap-3">
                <span className="font-mono text-xs uppercase text-coral">{item.type.replace("_", " ")}</span>
                <span className="text-xs text-ink/50">{formatDate(item.created_at)}</span>
              </div>
              <p className="mt-2 text-ink/75">{item.message}</p>
            </div>
          ))}
        </ReviewPanel>

        <ReviewPanel title="Translation Ratings" empty="No ratings yet.">
          {ratings.map((item) => (
            <div key={item.id} className="rounded border border-ink/10 p-3 text-sm">
              <p className="font-medium">Translation {item.translation_quality}/5 · Video {item.video_quality}/5</p>
              {item.comment ? <p className="mt-2 text-ink/70">{item.comment}</p> : null}
              <p className="mt-2 text-xs text-ink/50">{formatDate(item.created_at)}</p>
            </div>
          ))}
        </ReviewPanel>

        <ReviewPanel title="Bug Reports" empty="No bug reports yet.">
          {bugReports.map((item) => (
            <div key={item.id} className="rounded border border-ink/10 p-3 text-sm">
              <span className="font-mono text-xs uppercase text-coral">{item.category}</span>
              <p className="mt-2 text-ink/75">{item.description}</p>
              <p className="mt-2 text-xs text-ink/50">{formatDate(item.created_at)}</p>
            </div>
          ))}
        </ReviewPanel>
      </section>

      <section className="mt-6 grid gap-6 lg:grid-cols-3">
        <ReviewPanel title="Most Viewed News" empty="No views yet.">
          {analytics.most_viewed.map((item) => (
            <div key={item.article_id} className="rounded bg-canvas p-3 text-sm">
              <p className="line-clamp-2 font-medium">{item.title}</p>
              <p className="mt-1 text-xs text-ink/55">{item.views} views</p>
            </div>
          ))}
        </ReviewPanel>

        <ReviewPanel title="Search Topics" empty="No searches yet.">
          {analytics.search_topics.map((item) => (
            <div key={item.query} className="flex justify-between rounded bg-canvas px-3 py-2 text-sm">
              <span>{item.query}</span>
              <span>{item.searches}</span>
            </div>
          ))}
        </ReviewPanel>

        <ReviewPanel title="Engagement" empty="No engagement yet.">
          {analytics.engagement.map((item) => (
            <div key={item.label} className="flex justify-between rounded bg-canvas px-3 py-2 text-sm">
              <span>{item.label}</span>
              <span>{item.value}</span>
            </div>
          ))}
        </ReviewPanel>
      </section>
    </main>
  );
}

function ReviewPanel({ title, empty, children }: { title: string; empty: string; children: ReactNode }) {
  const hasChildren = Array.isArray(children) ? children.length > 0 : Boolean(children);
  return (
    <div className="rounded border border-ink/10 bg-white p-5 shadow-soft">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="mt-4 grid gap-3">{hasChildren ? children : <p className="text-sm text-ink/60">{empty}</p>}</div>
    </div>
  );
}
