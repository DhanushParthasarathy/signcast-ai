"use client";

import { FormEvent, useState } from "react";
import { MessageSquareWarning, Send, Star } from "lucide-react";

import { submitBugReport, submitFeedback, submitTranslationRating } from "@/lib/api";

interface FeedbackFormProps {
  articleId?: string;
}

export function FeedbackForm({ articleId }: FeedbackFormProps) {
  const [feedbackType, setFeedbackType] = useState("incorrect_gloss");
  const [translationQuality, setTranslationQuality] = useState(4);
  const [videoQuality, setVideoQuality] = useState(4);
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setStatus(null);
    try {
      await submitFeedback({
        article_id: articleId,
        feedback_type: feedbackType,
        message
      });
      await submitTranslationRating({
        article_id: articleId,
        translation_quality: translationQuality,
        video_quality: videoQuality,
        comment: message
      });
      if (feedbackType === "incorrect_sign") {
        await submitBugReport({
          article_id: articleId,
          category: "video",
          description: message
        });
      }
      setMessage("");
      setStatus("Feedback sent. Thank you for helping improve SignCast AI.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Feedback could not be submitted.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="rounded border border-ink/10 bg-white p-6 shadow-soft">
      <h2 className="flex items-center gap-2 text-xl font-semibold">
        <MessageSquareWarning size={20} aria-hidden="true" />
        Feedback
      </h2>
      <form onSubmit={submit} className="mt-5 grid gap-4">
        <label className="grid gap-2 text-sm font-medium">
          Feedback type
          <select
            value={feedbackType}
            onChange={(event) => setFeedbackType(event.target.value)}
            className="rounded border border-ink/15 bg-white px-3 py-2"
          >
            <option value="incorrect_gloss">Incorrect gloss</option>
            <option value="incorrect_sign">Incorrect sign</option>
            <option value="general">General feedback</option>
          </select>
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          <RatingInput label="Translation quality" value={translationQuality} onChange={setTranslationQuality} />
          <RatingInput label="Video quality" value={videoQuality} onChange={setVideoQuality} />
        </div>

        <label className="grid gap-2 text-sm font-medium">
          Notes
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            minLength={5}
            maxLength={2000}
            required
            rows={4}
            className="rounded border border-ink/15 px-3 py-2"
            placeholder="Tell us what looked wrong or what could be clearer."
          />
        </label>

        <button
          disabled={isSubmitting}
          className="flex items-center justify-center gap-2 rounded bg-ink px-4 py-2 font-medium text-canvas disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Send size={17} aria-hidden="true" />
          {isSubmitting ? "Sending" : "Send Feedback"}
        </button>
        {status ? <p className="rounded bg-canvas p-3 text-sm text-ink/70">{status}</p> : null}
      </form>
    </section>
  );
}

function RatingInput({
  label,
  value,
  onChange
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="grid gap-2 text-sm font-medium">
      {label}
      <span className="flex items-center gap-3 rounded border border-ink/15 px-3 py-2">
        <Star size={16} aria-hidden="true" className="text-coral" />
        <input
          type="range"
          min={1}
          max={5}
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
          className="w-full"
        />
        <span className="w-4 text-right tabular-nums">{value}</span>
      </span>
    </label>
  );
}
