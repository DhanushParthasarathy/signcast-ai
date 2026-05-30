export default function AccessibilityPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-normal text-coral">Accessibility</p>
      <h1 className="mt-3 text-4xl font-semibold">Accessibility Statement</h1>
      <div className="mt-6 space-y-4 leading-7 text-ink/70">
        <p>
          SignCast AI is designed for Deaf and hard-of-hearing users, sign-language learners, and
          readers who benefit from plain-language news.
        </p>
        <p>
          The interface uses semantic HTML, visible focus states, keyboard-accessible controls,
          readable contrast, captions-friendly video playback, and feedback paths for reporting
          incorrect glosses or signs.
        </p>
        <p>
          We review reported accessibility issues as launch blockers when they prevent users from
          reading, searching, saving, or playing translated news.
        </p>
      </div>
    </main>
  );
}
