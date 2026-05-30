const items = [
  {
    question: "Does SignCast AI generate sign language motion with AI?",
    answer: "No. The production MVP maps ASL gloss tokens to reviewed prerecorded sign clips."
  },
  {
    question: "What happens when a sign clip is missing?",
    answer: "The missing token is tracked for admins so the dictionary can be expanded."
  },
  {
    question: "Can I save articles?",
    answer: "Yes. The dashboard includes saved articles, bookmarks, watch history, and preferences."
  },
  {
    question: "Are summaries a substitute for the original article?",
    answer: "No. Each article page links to the original source for full context."
  }
];

export default function FAQPage() {
  return (
    <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <p className="text-sm font-semibold uppercase tracking-normal text-coral">FAQ</p>
      <h1 className="mt-3 text-4xl font-semibold">Common Questions</h1>
      <div className="mt-8 divide-y divide-ink/10 rounded border border-ink/10 bg-white shadow-soft">
        {items.map((item) => (
          <section key={item.question} className="p-5">
            <h2 className="text-lg font-semibold">{item.question}</h2>
            <p className="mt-2 leading-7 text-ink/70">{item.answer}</p>
          </section>
        ))}
      </div>
    </main>
  );
}
