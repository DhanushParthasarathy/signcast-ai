"use client";

import { useRouter, useSearchParams } from "next/navigation";

import type { NewsCategory } from "@/types/api";

const categories: NewsCategory[] = [
  "general",
  "business",
  "health",
  "science",
  "technology",
  "entertainment",
  "sports"
];

export function CategoryFilter({ active }: { active: NewsCategory }) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function selectCategory(category: NewsCategory) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("category", category);
    router.push(`/?${params.toString()}`);
  }

  return (
    <div className="flex flex-wrap gap-2" aria-label="News categories">
      {categories.map((category) => (
        <button
          key={category}
          type="button"
          onClick={() => selectCategory(category)}
          className={`rounded border px-3 py-2 text-sm capitalize transition ${
            active === category
              ? "border-ink bg-ink text-canvas"
              : "border-ink/15 bg-white text-ink/75 hover:border-ink/40"
          }`}
        >
          {category}
        </button>
      ))}
    </div>
  );
}
