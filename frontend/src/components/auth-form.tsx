"use client";

import { FormEvent, useState } from "react";
import { LogIn, UserPlus } from "lucide-react";

import { supabase } from "@/lib/supabase";

type AuthMode = "login" | "signup";

export function AuthForm() {
  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    if (!supabase) {
      setMessage("Supabase environment variables are not configured.");
      return;
    }

    setIsLoading(true);
    const result =
      mode === "login"
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });
    setIsLoading(false);

    if (result.error) {
      setMessage(result.error.message);
      return;
    }
    setMessage(mode === "login" ? "Signed in successfully." : "Check your email to confirm your account.");
  }

  return (
    <section className="mx-auto w-full max-w-md rounded border border-ink/10 bg-white p-6 shadow-soft">
      <div className="mb-5 flex rounded border border-ink/10 bg-canvas p-1">
        {(["login", "signup"] as const).map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setMode(item)}
            className={`flex-1 rounded px-3 py-2 text-sm font-medium capitalize ${
              mode === item ? "bg-ink text-canvas" : "text-ink/65"
            }`}
          >
            {item}
          </button>
        ))}
      </div>
      <form onSubmit={submit} className="grid gap-4">
        <label className="grid gap-2 text-sm font-medium">
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            className="rounded border border-ink/15 px-3 py-2"
          />
        </label>
        <label className="grid gap-2 text-sm font-medium">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={8}
            className="rounded border border-ink/15 px-3 py-2"
          />
        </label>
        <button
          type="submit"
          disabled={isLoading}
          className="flex items-center justify-center gap-2 rounded bg-coral px-4 py-2 font-medium text-white disabled:opacity-60"
        >
          {mode === "login" ? <LogIn size={17} aria-hidden="true" /> : <UserPlus size={17} aria-hidden="true" />}
          {isLoading ? "Working" : mode === "login" ? "Sign In" : "Create Account"}
        </button>
      </form>
      {message ? <p className="mt-4 rounded bg-canvas p-3 text-sm text-ink/70">{message}</p> : null}
    </section>
  );
}
