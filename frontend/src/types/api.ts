export type NewsCategory =
  | "general"
  | "business"
  | "entertainment"
  | "health"
  | "science"
  | "sports"
  | "technology";

export interface Article {
  id: string;
  source_name: string;
  author?: string | null;
  title: string;
  description?: string | null;
  content?: string | null;
  url: string;
  image_url?: string | null;
  published_at: string;
  category: NewsCategory;
}

export interface SignSequenceItem {
  token: string;
  clip_url?: string | null;
  status: "ready" | "missing" | string;
}

export interface ArticleDetail {
  article: Article;
  simplified_summary?: string | null;
  asl_gloss?: string | null;
  sign_sequence: SignSequenceItem[];
}

export interface NewsResponse {
  articles: Article[];
}

export interface SavedArticleItem {
  id: string;
  article: Article;
  bookmarked: boolean;
  created_at: string;
  updated_at: string;
}

export interface SavedArticlesResponse {
  items: SavedArticleItem[];
  total: number;
}

export interface WatchHistoryItem {
  id: string;
  article: Article;
  completed: boolean;
  duration_seconds: number;
  watched_at: string;
}

export interface WatchHistoryResponse {
  items: WatchHistoryItem[];
  total: number;
}

export interface UserPreferences {
  favorite_categories: NewsCategory[];
  preferred_language: string;
  captions_enabled: boolean;
  playback_speed: number;
}

export interface SignDictionaryEntry {
  id: string;
  gloss: string;
  video_url: string;
  thumbnail_url?: string | null;
  created_at: string;
}

export interface SignDictionaryListResponse {
  entries: SignDictionaryEntry[];
  total: number;
}

export interface AdminMetric {
  label: string;
  value: number;
}

export interface AdminCategoryUsage {
  category: string;
  views: number;
}

export interface ArticleViewMetric {
  article_id: string;
  title: string;
  views: number;
}

export interface SearchTopicMetric {
  query: string;
  searches: number;
}

export interface MissingGloss {
  gloss: string;
  occurrences: number;
}

export interface GenerationFailure {
  id: string;
  gloss_tokens: string[];
  error_message?: string | null;
  attempts: number;
  updated_at: string;
}

export interface AdminAnalytics {
  metrics: AdminMetric[];
  category_usage: AdminCategoryUsage[];
  most_viewed: ArticleViewMetric[];
  search_topics: SearchTopicMetric[];
  engagement: AdminMetric[];
  recent_failures: GenerationFailure[];
}

export interface MissingGlossResponse {
  items: MissingGloss[];
  total: number;
}

export interface FeedbackItem {
  id: string;
  type: "incorrect_gloss" | "incorrect_sign" | "general" | string;
  article_id?: string | null;
  message: string;
  status: string;
  created_at: string;
}

export interface TranslationRatingItem {
  id: string;
  article_id?: string | null;
  translation_quality: number;
  video_quality: number;
  comment?: string | null;
  created_at: string;
}

export interface BugReportItem {
  id: string;
  article_id?: string | null;
  category: string;
  description: string;
  status: string;
  created_at: string;
}
