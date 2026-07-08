"use client";

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  index: number;
}

export default function FeatureCard({
  title,
  description,
  index,
}: FeatureCardProps) {
  return (
    <article className="flex gap-5 py-4 first:pt-0 last:pb-0">
      <span className="font-mono text-xs text-text-muted w-5 shrink-0 pt-0.5">
        {String(index).padStart(2, "0")}
      </span>
      <div className="min-w-0">
        <h3 className="text-sm font-medium text-text-primary mb-1 tracking-[-0.01em]">
          {title}
        </h3>
        <p className="text-sm text-text-secondary leading-relaxed">
          {description}
        </p>
      </div>
    </article>
  );
}
