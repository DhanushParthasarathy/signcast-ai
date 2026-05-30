import { Suspense } from "react";
import { Accessibility, Newspaper, SearchX, Video } from "lucide-react";

import { ArticleCard } from "@/components/article-card";
import { CategoryFilter } from "@/components/category-filter";
import { EmptyState } from "@/components/empty-state";
import { MetricCard } from "@/components/metric-card";
import { SearchNews } from "@/components/search-news";
import { getNews } from "@/lib/api";
import type { NewsCategory } from "@/types/api";

interface HomeProps {
  searchParams: Promise<{ category?: NewsCategory; q?: string }>;
}

export default async function Home({ searchParams }: HomeProps) {
  const params = await searchParams;
  const category = params.category ?? "general";
  const articles = await getNews(category, params.q);
  const headline = params.q ? `Search results for "${params.q}"` : "Trending News";

  return (
    <main>
      <section className="border-b border-ink/10 bg-white">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_420px] lg:px-8">
          <div>
            <p className="text-sm font-semibold uppercase tracking-normal text-coral">Accessible news</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl">
              News translated into simple English, ASL gloss, and sign clip sequences.
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-ink/65">
              SignCast AI converts news into accessible sign-language-friendly content using AI-powered
              summarization and ASL gloss translation.
            </p>
            <p className="mt-3 max-w-2xl text-base leading-7 text-ink/65">
              Browse current headlines with an accessibility-first reading flow designed for Deaf and
              hard-of-hearing users, sign language students, and plain-language news readers.
            </p>
          </div>
          <div className="flex items-end">
            <Suspense>
              <SearchNews />
            </Suspense>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <MetricCard icon={Newspaper} label="Articles processed" value={String(articles.length)} tone="mint" />
          <MetricCard icon={Accessibility} label="Plain-language summaries" value="Ready" tone="coral" />
          <MetricCard icon={Video} label="Dictionary video playback" value="MVP" tone="berry" />
        </div>

        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold">{headline}</h2>
            <p className="mt-1 text-sm text-ink/60">Fetches latest headlines automatically from NewsAPI.</p>
          </div>
          <Suspense>
            <CategoryFilter active={category} />
          </Suspense>
        </div>

        {articles.length ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        ) : (
          <EmptyState
            icon={SearchX}
            title="No articles found"
            description="Try another search term or switch categories to fetch a new set of headlines."
          />
        )}
      </section>
    </main>
  );
}
