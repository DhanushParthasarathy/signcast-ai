import { FeedbackForm } from "@/components/feedback-form";

export default function ContactPage() {
  return (
    <main className="mx-auto grid max-w-5xl gap-6 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_420px] lg:px-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-normal text-coral">Contact</p>
        <h1 className="mt-3 text-4xl font-semibold">Tell us what needs attention.</h1>
        <p className="mt-5 leading-7 text-ink/70">
          Use the form to report incorrect glosses, incorrect signs, playback problems, or general
          product feedback. Reports appear in the admin review queue.
        </p>
      </section>
      <FeedbackForm />
    </main>
  );
}
