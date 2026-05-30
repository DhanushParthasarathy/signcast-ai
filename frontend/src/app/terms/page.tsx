export default function TermsPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-normal text-coral">Terms</p>
      <h1 className="mt-3 text-4xl font-semibold">Terms of Service</h1>
      <div className="mt-6 space-y-4 leading-7 text-ink/70">
        <p>
          SignCast AI provides accessibility-focused summaries, simplified English, ASL gloss, and
          sign-clip playback for informational use.
        </p>
        <p>
          Outputs may contain errors and should be reviewed against the original source article. Users
          must not upload copyrighted, harmful, or misleading sign clips.
        </p>
        <p>
          Admin uploads and generated sequences may be removed if they violate content, safety, or
          accessibility quality standards.
        </p>
      </div>
    </main>
  );
}
