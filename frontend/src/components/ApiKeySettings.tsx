"use client";

import { useEffect, useState } from "react";
import { Eye, EyeOff, ExternalLink, Check, Trash2, X } from "lucide-react";
import clsx from "clsx";
import {
  getStoredApiKey,
  setStoredApiKey,
  clearStoredApiKey,
  maskApiKey,
} from "@/lib/api-key";

interface ApiKeySettingsProps {
  open: boolean;
  onClose: () => void;
  onSaved?: () => void;
}

export default function ApiKeySettings({
  open,
  onClose,
  onSaved,
}: ApiKeySettingsProps) {
  const [value, setValue] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (open) {
      setValue(getStoredApiKey() ?? "");
      setSaved(false);
      setShowKey(false);
    }
  }, [open]);

  if (!open) return null;

  const handleSave = () => {
    const trimmed = value.trim();
    if (!trimmed) return;
    setStoredApiKey(trimmed);
    setSaved(true);
    onSaved?.();
    setTimeout(() => {
      onClose();
      setSaved(false);
    }, 600);
  };

  const handleClear = () => {
    clearStoredApiKey();
    setValue("");
    onSaved?.();
  };

  const storedKey = getStoredApiKey();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
        aria-label="Close settings"
      />
      <div
        className="relative w-full max-w-sm bg-surface border border-border animate-fade-in rounded-[var(--radius)]"
        role="dialog"
        aria-labelledby="api-key-title"
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 id="api-key-title" className="text-sm font-medium text-text-primary">
            Gemini API key
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-text-muted hover:text-text-primary"
            aria-label="Close"
          >
            <X className="w-4 h-4" strokeWidth={1.5} />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <p className="text-sm text-text-secondary leading-relaxed">
            Stored in your browser only. Sent with requests, not saved server-side.
          </p>

          {storedKey && (
            <div className="bg-bg-secondary px-3 py-2 text-xs text-text-secondary font-mono">
              {maskApiKey(storedKey)}
            </div>
          )}

          <div>
            <label htmlFor="gemini-api-key" className="ui-label block mb-2">
              Key
            </label>
            <div className="relative">
              <input
                id="gemini-api-key"
                type={showKey ? "text" : "password"}
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="AIza…"
                className="md-input pr-10 font-mono text-xs"
                autoComplete="off"
                spellCheck={false}
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-text-muted hover:text-text-primary"
                aria-label={showKey ? "Hide key" : "Show key"}
              >
                {showKey ? (
                  <EyeOff className="w-3.5 h-3.5" strokeWidth={1.5} />
                ) : (
                  <Eye className="w-3.5 h-3.5" strokeWidth={1.5} />
                )}
              </button>
            </div>
          </div>

          <a
            href="https://aistudio.google.com/apikey"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-text-secondary hover:text-text-primary border-b border-border hover:border-text-primary transition-colors"
          >
            Get a key
            <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
          </a>
        </div>

        <div className="flex items-center justify-between gap-2 px-4 py-3 border-t border-border">
          {storedKey ? (
            <button
              onClick={handleClear}
              className="md-btn-text text-danger text-xs"
            >
              <Trash2 className="w-3.5 h-3.5" strokeWidth={1.5} />
              Remove
            </button>
          ) : (
            <span />
          )}
          <div className="flex gap-2">
            <button onClick={onClose} className="md-btn-text text-xs">
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!value.trim()}
              className={clsx(
                "md-btn-filled text-xs",
                !value.trim() && "opacity-40 cursor-not-allowed"
              )}
            >
              {saved ? (
                <>
                  <Check className="w-3.5 h-3.5" strokeWidth={1.5} />
                  Saved
                </>
              ) : (
                "Save"
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
