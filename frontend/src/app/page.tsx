"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import AppShell from "@/components/AppShell";
import FeatureCard from "@/components/FeatureCard";
import PipelineStatus from "@/components/PipelineStatus";
import { FEATURES, SUGGESTED_PROMPTS } from "@/lib/constants";

const NOTES = [
  {
    n: "01",
    title: "Parallel data pull",
    body: "Price, technicals, fundamentals, and sentiment run at the same time.",
  },
  {
    n: "02",
    title: "Sequential synthesis",
    body: "Thesis and export steps wait until upstream agents finish.",
  },
  {
    n: "03",
    title: "Guardrails",
    body: "Ticker checks, crypto rejection, distressed-name limits.",
  },
  {
    n: "04",
    title: "Scoring model",
    body: "50% fundamentals · 40% technicals · 10% sentiment.",
  },
];

export default function HomePage() {
  return (
    <AppShell>
      <div className="flex-1 overflow-y-auto">
        <section className="border-b border-border">
          <div className="max-w-3xl mx-auto px-6 py-12 sm:py-16">
            <p className="ui-label mb-4">Quant research</p>
            <h1 className="text-[2rem] sm:text-[2.5rem] font-semibold leading-[1.1] tracking-[-0.03em] text-text-primary mb-4">
              Stock analysis,
              <br />
              start to finish.
            </h1>
            <p className="text-[0.9375rem] text-text-secondary max-w-md mb-8 leading-relaxed">
              Feed a ticker. Get technicals, fundamentals, sentiment, a written
              thesis, and exportable reports.
            </p>
            <div className="flex flex-wrap items-center gap-3 mb-10">
              <Link href="/chat" className="md-btn-filled">
                Open chat
                <ArrowUpRight className="w-3.5 h-3.5" strokeWidth={1.5} />
              </Link>
              <Link href="/artifacts" className="md-btn-outlined">
                View exports
              </Link>
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <Link
                  key={prompt}
                  href={`/chat?q=${encodeURIComponent(prompt)}`}
                  className="md-chip font-mono text-xs"
                >
                  {prompt}
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className="border-b border-border bg-surface">
          <div className="max-w-3xl mx-auto px-6 py-10">
            <p className="ui-label mb-5">What it does</p>
            <div className="divide-y divide-border">
              {FEATURES.map((feature, i) => (
                <FeatureCard key={feature.id} index={i + 1} {...feature} />
              ))}
            </div>
          </div>
        </section>

        <section className="max-w-3xl mx-auto px-6 py-10">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <p className="ui-label mb-5">Under the hood</p>
              <div className="space-y-5">
                {NOTES.map(({ n, title, body }) => (
                  <div key={n} className="flex gap-4">
                    <span className="font-mono text-xs text-text-muted pt-0.5 w-5 shrink-0">
                      {n}
                    </span>
                    <div>
                      <h3 className="text-sm font-medium text-text-primary mb-0.5">
                        {title}
                      </h3>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        {body}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="ui-label mb-5">Run order</p>
              <PipelineStatus
                completedSteps={[
                  "validate",
                  "price",
                  "technicals",
                  "fundamentals",
                  "sentiment",
                  "thesis",
                  "export",
                ]}
              />
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
