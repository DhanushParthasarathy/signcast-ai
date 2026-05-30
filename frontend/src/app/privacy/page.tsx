export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-normal text-coral">Privacy</p>
      <h1 className="mt-3 text-4xl font-semibold">Privacy Policy</h1>
      <div className="mt-6 space-y-4 leading-7 text-ink/70">
        <p>
          SignCast AI stores account information, saved articles, watch history, preferences,
          feedback, ratings, and operational logs needed to run the service.
        </p>
        <p>
          News content is fetched from configured providers. AI summarization requests may send article
          text to the configured LLM provider. Secrets and service-role keys are stored only in the
          deployment provider environment.
        </p>
        <p>
          Users can request deletion or correction of account-linked data through the contact page.
        </p>
      </div>
    </main>
  );
}
