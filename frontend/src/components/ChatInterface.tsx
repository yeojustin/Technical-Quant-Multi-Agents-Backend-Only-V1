"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Send, Loader2, AlertCircle, FileBox, Key } from "lucide-react";
import clsx from "clsx";
import MessageBubble from "./MessageBubble";
import PipelineStatus from "./PipelineStatus";
import { SUGGESTED_PROMPTS } from "@/lib/constants";
import { createSession, streamAgent } from "@/lib/adk-api";
import { DEFAULT_USER_ID } from "@/lib/constants";
import { hasApiKey } from "@/lib/api-key";
import type { ChatMessage } from "@/lib/types";

interface ChatInterfaceProps {
  sessionId: string | null;
  userId?: string;
  initialQuery?: string | null;
  onSessionCreated?: (sessionId: string) => void;
  onArtifactsUpdated?: () => void;
  showArtifactToggle?: boolean;
  onToggleArtifacts?: () => void;
}

function generateSessionId() {
  return `s_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export default function ChatInterface({
  sessionId: externalSessionId,
  userId = DEFAULT_USER_ID,
  initialQuery,
  onSessionCreated,
  onArtifactsUpdated,
  showArtifactToggle,
  onToggleArtifacts,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<string | undefined>();
  const [completedSteps, setCompletedSteps] = useState<string[]>([]);
  const [internalSessionId, setInternalSessionId] = useState<string | null>(
    externalSessionId
  );

  const sessionId = externalSessionId ?? internalSessionId;
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setInternalSessionId(externalSessionId);
  }, [externalSessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const initialQuerySent = useRef(false);

  const ensureSession = useCallback(async () => {
    if (sessionId) return sessionId;
    const newId = generateSessionId();
    await createSession(userId, newId);
    setInternalSessionId(newId);
    onSessionCreated?.(newId);
    return newId;
  }, [sessionId, userId, onSessionCreated]);

  const mapAuthorToStep = (author: string): string | undefined => {
    const map: Record<string, string> = {
      price_feed_agent: "price",
      indicator_agent_pipeline: "technicals",
      fundamental_agent_pipeline: "fundamentals",
      sentiment_agent_pipeline: "sentiment",
      master_analysis_agent: "thesis",
      exporter_agent: "export",
      QuantPortfolioPipeline: "validate",
      parallel_agent: "price",
      root_agent: "validate",
    };
    return map[author];
  };

  const handleSend = async (text?: string) => {
    const messageText = (text ?? input).trim();
    if (!messageText || isLoading) return;

    if (!hasApiKey()) {
      setError(
        "Add your Gemini API key first — open API Key in the sidebar."
      );
      return;
    }

    setInput("");
    setError(null);
    setIsLoading(true);
    setActiveStep("validate");
    setCompletedSteps([]);

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}`,
      role: "user",
      content: messageText,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);

    const assistantId = `msg_${Date.now()}_assistant`;
    setMessages((prev) => [
      ...prev,
      {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: Date.now(),
        isStreaming: true,
      },
    ]);

    try {
      const sid = await ensureSession();
      let accumulatedText = "";
      const seenSteps = new Set<string>();

      for await (const event of streamAgent(userId, sid, messageText)) {
        const step = mapAuthorToStep(event.author);
        if (step) {
          setActiveStep(step);
          if (!seenSteps.has(step)) {
            seenSteps.add(step);
            setCompletedSteps((prev) => {
              if (prev.includes(step)) return prev;
              return [...prev, step];
            });
          }
        }

        if (event.actions?.artifactDelta) {
          onArtifactsUpdated?.();
        }

        if (event.content?.parts) {
          for (const part of event.content.parts) {
            if (part.text && event.content.role === "model") {
              accumulatedText += part.text;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: accumulatedText, author: event.author }
                    : m
                )
              );
            }
          }
        }
      }

      setCompletedSteps([
        "validate",
        "price",
        "technicals",
        "fundamentals",
        "sentiment",
        "thesis",
        "export",
      ]);
      setActiveStep(undefined);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId ? { ...m, isStreaming: false } : m
        )
      );

      onArtifactsUpdated?.();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Analysis failed";
      setError(msg);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: `**Error:** ${msg}\n\nMake sure the ADK backend is running:\n\`\`\`bash\nuv run adk web\n\`\`\``,
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  useEffect(() => {
    if (initialQuery && !initialQuerySent.current && messages.length === 0) {
      initialQuerySent.current = true;
      handleSend(initialQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuery]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setError(null);
    setActiveStep(undefined);
    setCompletedSteps([]);
    setInternalSessionId(null);
  };

  return (
    <div className="flex flex-col h-full bg-bg-primary">
      <header className="md-app-bar flex items-center justify-between h-11 px-4 shrink-0">
        <div>
          <h1 className="text-sm font-medium text-text-primary tracking-[-0.01em]">Chat</h1>
          <p className="font-mono text-[10px] text-text-muted truncate max-w-[220px]">
            {sessionId ? sessionId.slice(0, 18) + "…" : "no session"}
          </p>
        </div>
        <div className="flex items-center gap-1">
          {showArtifactToggle && (
            <button onClick={onToggleArtifacts} className="md-btn-text text-xs">
              <FileBox className="w-4 h-4" />
              Artifacts
            </button>
          )}
          <button onClick={handleNewChat} className="md-btn-text text-xs">
            Clear
          </button>
        </div>
      </header>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
            {messages.length === 0 ? (
              <div className="max-w-xl">
                <p className="ui-label mb-3">New analysis</p>
                <h2 className="text-lg font-semibold tracking-[-0.02em] text-text-primary mb-2">
                  Enter a ticker
                </h2>
                <p className="text-sm text-text-secondary mb-6 leading-relaxed">
                  Try one of the examples below, or type your own prompt.
                </p>
                {!hasApiKey() && (
                  <div className="flex items-start gap-2 border border-warning bg-[var(--signal-muted)] px-3 py-2.5 mb-6 text-xs text-[var(--signal)]">
                    <Key className="w-3.5 h-3.5 shrink-0 mt-0.5" strokeWidth={1.5} />
                    <span>Set your Gemini API key in the sidebar first.</span>
                  </div>
                )}
                <div className="flex flex-wrap gap-x-4 gap-y-1">
                  {SUGGESTED_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => handleSend(prompt)}
                      className="md-chip font-mono text-xs"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="max-w-2xl mx-auto space-y-4">
                {messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {error && (
            <div className="mx-4 mb-2 flex items-center gap-2 border border-danger/30 bg-surface px-4 py-2.5">
              <AlertCircle className="w-4 h-4 text-danger shrink-0" />
              <p className="text-xs text-danger">{error}</p>
            </div>
          )}

          <div className="p-2 sm:p-3 border-t border-border bg-surface">
            <div className="max-w-2xl mx-auto">
              <div className="flex items-end gap-2 border border-border-strong bg-surface p-1.5 focus-within:border-primary">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Analyze AAPL…"
                  rows={1}
                  disabled={isLoading}
                  className="flex-1 resize-none bg-transparent px-2 py-1.5 text-xs sm:text-sm text-text-primary placeholder:text-text-muted focus:outline-none disabled:opacity-50"
                  style={{ maxHeight: "120px" }}
                />
                <button
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className={clsx(
                    "p-1.5 transition-colors shrink-0",
                    input.trim() && !isLoading
                      ? "bg-primary text-on-primary hover:bg-primary-hover"
                      : "bg-bg-tertiary text-text-disabled cursor-not-allowed"
                  )}
                  aria-label="Send message"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </div>
              <p className="text-[10px] text-text-muted text-center mt-1">
                Equities only
              </p>
            </div>
          </div>
        </div>

        {isLoading && (
          <div className="w-44 border-l border-border p-2 hidden lg:block bg-surface shrink-0">
            <PipelineStatus
              activeStep={activeStep}
              completedSteps={completedSteps}
            />
          </div>
        )}
      </div>
    </div>
  );
}
