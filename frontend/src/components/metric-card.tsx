import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string;
  tone: "mint" | "coral" | "berry";
}

const tones = {
  mint: "bg-mint/20 text-ink",
  coral: "bg-coral/15 text-coral",
  berry: "bg-berry/15 text-berry"
};

export function MetricCard({ icon: Icon, label, value, tone }: MetricCardProps) {
  return (
    <div className="rounded border border-ink/10 bg-white p-5 shadow-soft">
      <div className={`flex h-10 w-10 items-center justify-center rounded ${tones[tone]}`}>
        <Icon size={18} aria-hidden="true" />
      </div>
      <p className="mt-4 text-2xl font-semibold">{value}</p>
      <p className="mt-1 text-sm text-ink/60">{label}</p>
    </div>
  );
}
