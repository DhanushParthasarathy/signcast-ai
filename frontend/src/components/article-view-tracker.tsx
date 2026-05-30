"use client";

import { useEffect } from "react";

import { addWatchHistory } from "@/lib/api";

export function ArticleViewTracker({ articleId }: { articleId: string }) {
  useEffect(() => {
    const startedAt = Date.now();
    void addWatchHistory(articleId, false, 0);

    return () => {
      const durationSeconds = Math.max(Math.round((Date.now() - startedAt) / 1000), 1);
      void addWatchHistory(articleId, true, durationSeconds);
    };
  }, [articleId]);

  return null;
}
