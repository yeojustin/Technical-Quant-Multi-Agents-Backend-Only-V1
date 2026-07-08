"use client";

import MarkdownRenderer from "./MarkdownRenderer";
import clsx from "clsx";
import type { ChatMessage } from "@/lib/types";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={clsx(
        "animate-fade-in max-w-[92%]",
        isUser ? "ml-auto" : "mr-auto"
      )}
    >
      <div
        className={clsx(
          "px-3.5 py-2.5 text-sm",
          isUser
            ? "bg-primary text-on-primary rounded-[var(--radius)]"
            : "border border-border bg-surface rounded-[var(--radius)]"
        )}
      >
        {isUser ? (
          <p className="leading-relaxed whitespace-pre-wrap text-[0.8125rem]">
            {message.content}
          </p>
        ) : (
          <div className={clsx(message.isStreaming && "streaming-cursor")}>
            <MarkdownRenderer content={message.content} />
          </div>
        )}
        {message.author && !isUser && (
          <p className="font-mono text-[10px] text-text-muted mt-2">
            {message.author}
          </p>
        )}
      </div>
    </div>
  );
}
