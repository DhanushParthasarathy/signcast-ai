import type {
  AdminAnalytics,
  ArticleDetail,
  BugReportItem,
  FeedbackItem,
  GenerationFailure,
  MissingGlossResponse,
  NewsCategory,
  NewsResponse,
  SavedArticlesResponse,
  SignDictionaryEntry,
  SignDictionaryListResponse,
  TranslationRatingItem,
  UserPreferences,
  WatchHistoryResponse
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const USER_ID_KEY = "signcast:user-id";
const ADMIN_TOKEN_KEY = "signcast:admin-token";

function getUserId() {
  if (typeof window === "undefined") {
    return "00000000-0000-4000-8000-000000000001";
  }
  const existing = localStorage.getItem(USER_ID_KEY);
  if (existing) {
    return existing;
  }
  const id = crypto.randomUUID();
  localStorage.setItem(USER_ID_KEY, id);
  return id;
}

function userHeaders() {
  return {
    "Content-Type": "application/json",
    "X-User-Id": getUserId()
  };
}

export function getAdminToken() {
  if (typeof window === "undefined") {
    return "";
  }
  return localStorage.getItem(ADMIN_TOKEN_KEY) ?? "";
}

export function setAdminToken(token: string) {
  if (typeof window !== "undefined") {
    localStorage.setItem(ADMIN_TOKEN_KEY, token);
  }
}

function adminHeaders(contentType = true) {
  return {
    ...(contentType ? { "Content-Type": "application/json" } : {}),
    "X-Admin-Token": getAdminToken()
  };
}

export async function getNews(category: NewsCategory = "general", query?: string) {
  const params = new URLSearchParams({ category });
  if (query) {
    params.set("q", query);
  }
  const response = await fetch(`${API_BASE_URL}/news?${params.toString()}`, {
    next: { revalidate: 300 }
  });
  if (!response.ok) {
    throw new Error("Unable to load news");
  }
  const data = (await response.json()) as NewsResponse;
  return data.articles;
}

export async function getArticle(articleId: string) {
  const response = await fetch(`${API_BASE_URL}/news/${articleId}`, {
    next: { revalidate: 300 }
  });
  if (!response.ok) {
    throw new Error("Unable to load article");
  }
  return (await response.json()) as ArticleDetail;
}

export async function getSavedArticles(bookmarked?: boolean) {
  const params = new URLSearchParams();
  if (typeof bookmarked === "boolean") {
    params.set("bookmarked", String(bookmarked));
  }
  const response = await fetch(`${API_BASE_URL}/me/saved-articles?${params.toString()}`, {
    headers: userHeaders(),
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Unable to load saved articles");
  }
  return (await response.json()) as SavedArticlesResponse;
}

export async function saveArticle(articleId: string, bookmarked = false) {
  const response = await fetch(`${API_BASE_URL}/me/saved-articles`, {
    method: "POST",
    headers: userHeaders(),
    body: JSON.stringify({ article_id: articleId, bookmarked })
  });
  if (!response.ok) {
    throw new Error("Unable to save article");
  }
  return (await response.json()) as SavedArticlesResponse;
}

export async function unsaveArticle(articleId: string) {
  const response = await fetch(`${API_BASE_URL}/me/saved-articles/${articleId}`, {
    method: "DELETE",
    headers: userHeaders()
  });
  if (!response.ok) {
    throw new Error("Unable to remove saved article");
  }
}

export async function bookmarkArticle(articleId: string, bookmarked: boolean) {
  const response = await fetch(`${API_BASE_URL}/me/saved-articles/${articleId}/bookmark`, {
    method: "PUT",
    headers: userHeaders(),
    body: JSON.stringify({ bookmarked })
  });
  if (!response.ok) {
    throw new Error("Unable to update bookmark");
  }
  return (await response.json()) as SavedArticlesResponse;
}

export async function addWatchHistory(articleId: string, completed = false, durationSeconds = 0) {
  const response = await fetch(`${API_BASE_URL}/me/watch-history`, {
    method: "POST",
    headers: userHeaders(),
    body: JSON.stringify({
      article_id: articleId,
      completed,
      duration_seconds: durationSeconds
    })
  });
  if (!response.ok) {
    return null;
  }
  return (await response.json()) as WatchHistoryResponse;
}

export async function getRecentlyViewed() {
  const response = await fetch(`${API_BASE_URL}/me/recently-viewed`, {
    headers: userHeaders(),
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Unable to load recently viewed articles");
  }
  return (await response.json()) as WatchHistoryResponse;
}

export async function getPreferences() {
  const response = await fetch(`${API_BASE_URL}/me/preferences`, {
    headers: userHeaders(),
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Unable to load preferences");
  }
  return (await response.json()) as UserPreferences;
}

export async function updatePreferences(preferences: Partial<UserPreferences>) {
  const response = await fetch(`${API_BASE_URL}/me/preferences`, {
    method: "PUT",
    headers: userHeaders(),
    body: JSON.stringify(preferences)
  });
  if (!response.ok) {
    throw new Error("Unable to update preferences");
  }
  return (await response.json()) as UserPreferences;
}

export async function getSignDictionary(query?: string) {
  const params = new URLSearchParams();
  if (query) {
    params.set("q", query);
  }
  const response = await fetch(`${API_BASE_URL}/sign-dictionary?${params.toString()}`, {
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Unable to load sign dictionary");
  }
  return (await response.json()) as SignDictionaryListResponse;
}

export async function uploadSignClip(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/sign-dictionary`, {
    method: "POST",
    headers: adminHeaders(false),
    body: formData
  });
  if (!response.ok) {
    throw new Error("Unable to upload sign clip");
  }
  return (await response.json()) as SignDictionaryEntry;
}

export async function updateSignEntry(id: string, payload: Partial<SignDictionaryEntry>) {
  const response = await fetch(`${API_BASE_URL}/sign-dictionary/${id}`, {
    method: "PUT",
    headers: adminHeaders(),
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Unable to update sign entry");
  }
  return (await response.json()) as SignDictionaryEntry;
}

export async function deleteSignEntry(id: string) {
  const response = await fetch(`${API_BASE_URL}/sign-dictionary/${id}`, {
    method: "DELETE",
    headers: adminHeaders(false)
  });
  if (!response.ok) {
    throw new Error("Unable to delete sign entry");
  }
}

export async function getAdminAnalytics() {
  const response = await fetch(`${API_BASE_URL}/admin/analytics`, { headers: adminHeaders(false), cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load admin analytics");
  }
  return (await response.json()) as AdminAnalytics;
}

export async function getMissingGlosses() {
  const response = await fetch(`${API_BASE_URL}/admin/missing-glosses`, { headers: adminHeaders(false), cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load missing glosses");
  }
  return (await response.json()) as MissingGlossResponse;
}

export async function getGenerationFailures() {
  const response = await fetch(`${API_BASE_URL}/admin/generation-failures`, { headers: adminHeaders(false), cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load generation failures");
  }
  return (await response.json()) as GenerationFailure[];
}

export async function submitFeedback(payload: { article_id?: string; feedback_type: string; message: string }) {
  const response = await fetch(`${API_BASE_URL}/feedback`, {
    method: "POST",
    headers: userHeaders(),
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Unable to submit feedback");
  }
  return (await response.json()) as FeedbackItem;
}

export async function submitTranslationRating(payload: {
  article_id?: string;
  translation_quality: number;
  video_quality: number;
  comment?: string;
}) {
  const response = await fetch(`${API_BASE_URL}/translation-ratings`, {
    method: "POST",
    headers: userHeaders(),
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Unable to submit rating");
  }
  return (await response.json()) as TranslationRatingItem;
}

export async function submitBugReport(payload: { article_id?: string; category: string; description: string }) {
  const response = await fetch(`${API_BASE_URL}/bug-reports`, {
    method: "POST",
    headers: userHeaders(),
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("Unable to submit report");
  }
  return (await response.json()) as BugReportItem;
}

export async function getAdminFeedback() {
  const response = await fetch(`${API_BASE_URL}/admin/feedback`, { headers: adminHeaders(false), cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load feedback");
  }
  return (await response.json()) as FeedbackItem[];
}

export async function getAdminRatings() {
  const response = await fetch(`${API_BASE_URL}/admin/translation-ratings`, { headers: adminHeaders(false), cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load ratings");
  }
  return (await response.json()) as TranslationRatingItem[];
}

export async function getAdminBugReports() {
  const response = await fetch(`${API_BASE_URL}/admin/bug-reports`, { headers: adminHeaders(false), cache: "no-store" });
  if (!response.ok) {
    throw new Error("Unable to load bug reports");
  }
  return (await response.json()) as BugReportItem[];
}
