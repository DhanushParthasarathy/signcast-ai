export function GlossTokenList({ gloss }: { gloss?: string | null }) {
  const tokens = gloss?.split(/\s+/).filter(Boolean) ?? [];

  if (!tokens.length) {
    return <p className="text-sm text-ink/60">No ASL gloss has been generated yet.</p>;
  }

  return (
    <div className="flex flex-wrap gap-2" aria-label="ASL gloss token sequence">
      {tokens.map((token, index) => (
        <span
          key={`${token}-${index}`}
          className="rounded border border-ink/10 bg-canvas px-3 py-2 font-mono text-sm"
        >
          {token}
        </span>
      ))}
    </div>
  );
}
