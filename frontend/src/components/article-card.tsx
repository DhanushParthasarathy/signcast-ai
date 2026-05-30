import Link from "next/link";
import { ArrowRight, ImageOff, Newspaper } from "lucide-react";

import { formatDate } from "@/lib/format";
import type { Article } from "@/types/api";

export function ArticleCard({ article }: { article: Article }) {
  return (
    <Link
      href={`/articles/${article.id}`}
      className="group flex min-h-[360px] flex-col overflow-hidden rounded border border-ink/10 bg-white shadow-soft transition hover:-translate-y-0.5 hover:border-ink/25 focus:outline-none focus:ring-2 focus:ring-coral"
    >
      <div className="relative aspect-[16/9] bg-ink">
        {article.image_url ? (
          // NewsAPI image URLs are remote and dynamic; a native img keeps this deployment-provider neutral.
          <img src={article.image_url} alt="" className="h-full w-full object-cover" loading="lazy" />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-ink text-canvas/70">
            <ImageOff size={28} aria-hidden="true" />
          </div>
        )}
        <span className="absolute left-3 top-3 rounded bg-white/95 px-2 py-1 text-xs font-medium capitalize text-ink">
          {article.category}
        </span>
      </div>
      <div className="flex flex-1 flex-col justify-between p-5">
        <div>
          <div className="mb-4 flex items-center justify-between gap-3 text-xs uppercase tracking-normal text-steel">
            <span className="flex min-w-0 items-center gap-2">
              <Newspaper size={15} aria-hidden="true" />
              <span className="truncate">{article.source_name}</span>
            </span>
            <span className="shrink-0">{formatDate(article.published_at)}</span>
          </div>
          <h2 className="text-lg font-semibold leading-snug">{article.title}</h2>
          {article.description ? (
            <p className="mt-3 line-clamp-3 text-sm leading-6 text-ink/70">{article.description}</p>
          ) : null}
        </div>
        <span className="mt-5 flex items-center gap-2 text-sm font-medium text-berry">
          View SignCast
          <ArrowRight size={16} aria-hidden="true" className="transition group-hover:translate-x-1" />
        </span>
      </div>
    </Link>
  );
}
