export default function AboutPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-normal text-coral">About</p>
      <h1 className="mt-3 text-4xl font-semibold">Accessible news, built for clarity.</h1>
      <div className="mt-6 space-y-4 leading-7 text-ink/70">
        <p>
          SignCast AI converts news into accessible sign-language-friendly content using AI-powered
          summarization and ASL gloss translation.
        </p>
        <p>
          The MVP uses verified news sources, plain-language summaries, rule-based ASL gloss output,
          and a managed dictionary of prerecorded sign clips. It does not generate sign motion with AI
          in production.
        </p>
      </div>
    </main>
  );
}
