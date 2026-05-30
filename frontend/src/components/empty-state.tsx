import type { LucideIcon } from "lucide-react";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
}

export function EmptyState({ icon: Icon, title, description }: EmptyStateProps) {
  return (
    <div className="rounded border border-dashed border-ink/20 bg-white p-8 text-center">
      <div className="mx-auto flex h-12 w-12 items-center justify-center rounded bg-mint/20 text-ink">
        <Icon size={22} aria-hidden="true" />
      </div>
      <h2 className="mt-4 text-lg font-semibold">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-ink/60">{description}</p>
    </div>
  );
}
