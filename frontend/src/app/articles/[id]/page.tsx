import Link from "next/link";
import { ExternalLink, FileText, ImageOff, Languages } from "lucide-react";

import { ArticleViewTracker } from "@/components/article-view-tracker";
import { FeedbackForm } from "@/components/feedback-form";
import { GlossTokenList } from "@/components/gloss-token-list";
import { SaveArticleButton } from "@/components/save-article-button";
import { SignPlayer } from "@/components/sign-player";
import { getArticle } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

interface ArticlePageProps {
  params: Promise<{ id: string }>;
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { id } = await params;
  const detail = await getArticle(id);
  const { article } = detail;

  return (
    <main className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-[minmax(0,1fr)_420px] lg:px-8">
      <ArticleViewTracker articleId={article.id} />
      <article className="space-y-5">
        <div className="overflow-hidden rounded border border-ink/10 bg-white shadow-soft">
          <div className="relative aspect-[16/9] bg-ink">
            {article.image_url ? (
              <img src={article.image_url} alt="" className="h-full w-full object-cover" />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-canvas/70">
                <ImageOff size={34} aria-hidden="true" />
              </div>
            )}
          </div>
          <div className="p-6">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3 text-sm text-ink/60">
              <span>{article.source_name}</span>
              <span>{formatDateTime(article.published_at)}</span>
            </div>
            <h1 className="text-3xl font-semibold leading-tight">{article.title}</h1>
            {article.description ? <p className="mt-4 leading-7 text-ink/75">{article.description}</p> : null}
            <div className="mt-5 flex flex-wrap gap-2">
              <Link
                href={article.url}
                className="flex items-center gap-2 rounded bg-ink px-4 py-2 text-sm font-medium text-canvas transition hover:bg-ink/90"
              >
                <ExternalLink size={16} aria-hidden="true" />
                Original Article
              </Link>
              <SaveArticleButton article={article} />
            </div>
          </div>
        </div>

        <section className="rounded border border-ink/10 bg-white p-6 shadow-soft">
          <h2 className="flex items-center gap-2 text-xl font-semibold">
            <FileText size={20} aria-hidden="true" />
            Simplified Article
          </h2>
          <p className="mt-3 leading-7 text-ink/75">{detail.simplified_summary}</p>
        </section>

        <section className="rounded border border-ink/10 bg-white p-6 shadow-soft">
          <h2 className="flex items-center gap-2 text-xl font-semibold">
            <Languages size={20} aria-hidden="true" />
            ASL Gloss
          </h2>
          <div className="mt-4">
            <GlossTokenList gloss={detail.asl_gloss} />
          </div>
        </section>
        <FeedbackForm articleId={article.id} />
      </article>

      <aside className="lg:sticky lg:top-6 lg:self-start">
        <SignPlayer sequence={detail.sign_sequence} />
      </aside>
    </main>
  );
}
