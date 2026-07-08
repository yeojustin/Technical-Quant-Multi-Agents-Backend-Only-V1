"use client";

import { PIPELINE_STEPS } from "@/lib/constants";
import clsx from "clsx";

interface PipelineStatusProps {
  activeStep?: string;
  completedSteps?: string[];
}

export default function PipelineStatus({
  activeStep,
  completedSteps = [],
}: PipelineStatusProps) {
  return (
    <div className="border border-border bg-surface rounded-[var(--radius)] font-mono text-xs">
      {PIPELINE_STEPS.map((step, i) => {
        const isComplete = completedSteps.includes(step.id);
        const isActive = activeStep === step.id;
        const isLast = i === PIPELINE_STEPS.length - 1;

        return (
          <div
            key={step.id}
            className={clsx(
              "flex items-center gap-3 px-3 py-2",
              !isLast && "border-b border-border"
            )}
          >
            <span
              className={clsx(
                "w-4 text-right shrink-0",
                isComplete
                  ? "text-success"
                  : isActive
                    ? "text-text-primary"
                    : "text-text-muted"
              )}
            >
              {isComplete ? "✓" : isActive ? "…" : "·"}
            </span>
            <span
              className={clsx(
                isComplete || isActive
                  ? "text-text-primary"
                  : "text-text-muted"
              )}
            >
              {step.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
