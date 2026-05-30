export default function ArticleLoading() {
  return (
    <main className="mx-auto grid max-w-7xl gap-6 px-4 py-8 sm:px-6 lg:grid-cols-[minmax(0,1fr)_420px] lg:px-8">
      <div className="space-y-5">
        <div className="h-[420px] animate-pulse rounded border border-ink/10 bg-white" />
        <div className="h-40 animate-pulse rounded border border-ink/10 bg-white" />
        <div className="h-36 animate-pulse rounded border border-ink/10 bg-white" />
      </div>
      <div className="h-[420px] animate-pulse rounded border border-ink/10 bg-white" />
    </main>
  );
}
