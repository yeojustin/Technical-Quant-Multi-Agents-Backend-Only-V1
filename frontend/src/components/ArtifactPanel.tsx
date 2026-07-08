"use client";

import { useEffect, useState, useCallback } from "react";
import {
  FileText,
  FileSpreadsheet,
  Download,
  Trash2,
  RefreshCw,
  X,
  ExternalLink,
} from "lucide-react";
import clsx from "clsx";
import {
  listArtifacts,
  listArtifactVersions,
  getArtifactUrl,
  deleteArtifact,
} from "@/lib/adk-api";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { ArtifactVersion } from "@/lib/types";

interface ArtifactPanelProps {
  sessionId: string | null;
  userId?: string;
  onClose?: () => void;
  refreshTrigger?: number;
}

interface ArtifactDetail {
  name: string;
  versions: ArtifactVersion[];
}

export default function ArtifactPanel({
  sessionId,
  userId = DEFAULT_USER_ID,
  onClose,
  refreshTrigger = 0,
}: ArtifactPanelProps) {
  const [artifacts, setArtifacts] = useState<ArtifactDetail[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedArtifact, setSelectedArtifact] = useState<string | null>(null);

  const loadArtifacts = useCallback(async () => {
    if (!sessionId) {
      setArtifacts([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const names = await listArtifacts(userId, sessionId);
      const details = await Promise.all(
        names.map(async (name) => {
          try {
            const versions = await listArtifactVersions(
              userId,
              sessionId,
              name
            );
            return { name, versions };
          } catch {
            return { name, versions: [] };
          }
        })
      );
      setArtifacts(details);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load artifacts");
    } finally {
      setLoading(false);
    }
  }, [sessionId, userId]);

  useEffect(() => {
    loadArtifacts();
  }, [loadArtifacts, refreshTrigger]);

  const handleDelete = async (name: string) => {
    if (!sessionId) return;
    if (!confirm(`Delete artifact "${name}"?`)) return;
    try {
      await deleteArtifact(userId, sessionId, name);
      await loadArtifacts();
      if (selectedArtifact === name) setSelectedArtifact(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const getIcon = (name: string) => {
    const cls = "w-4 h-4 flat-icon shrink-0";
    if (name.endsWith(".pdf"))
      return <FileText className={cls} strokeWidth={1.5} />;
    if (name.endsWith(".xlsx"))
      return <FileSpreadsheet className={cls} strokeWidth={1.5} />;
    return <FileText className={cls} strokeWidth={1.5} />;
  };

  return (
    <aside className="w-56 border-l border-border bg-surface flex flex-col h-full shrink-0">
      <div className="flex items-center justify-between h-11 px-2 border-b border-border">
        <div>
          <h2 className="text-xs font-medium text-text-primary">Artifacts</h2>
          <p className="text-[10px] text-text-muted uppercase tracking-wide">
            Reports & exports
          </p>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={loadArtifacts}
            disabled={loading || !sessionId}
            className="p-2 hover:bg-bg-secondary text-text-muted disabled:opacity-40"
            aria-label="Refresh artifacts"
          >
            <RefreshCw
              className={clsx("w-4 h-4", loading && "animate-spin")}
            />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-bg-secondary text-text-muted"
              aria-label="Close panel"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {!sessionId ? (
          <div className="text-center py-8 px-2">
            <FileText className="w-5 h-5 flat-icon mx-auto mb-2" strokeWidth={1.5} />
            <p className="text-xs text-text-muted">
              Start an analysis to generate artifacts
            </p>
          </div>
        ) : loading && artifacts.length === 0 ? (
          <div className="text-center py-8">
            <RefreshCw className="w-4 h-4 text-text-muted animate-spin mx-auto mb-1.5" strokeWidth={1.5} />
            <p className="text-xs text-text-muted">Loading...</p>
          </div>
        ) : error ? (
          <div className="border border-danger/30 bg-surface p-3">
            <p className="text-xs text-danger">{error}</p>
          </div>
        ) : artifacts.length === 0 ? (
          <div className="text-center py-8 px-2">
            <FileText className="w-5 h-5 flat-icon mx-auto mb-2" strokeWidth={1.5} />
            <p className="text-xs text-text-muted">
              No artifacts yet. Run analysis for PDF/Excel exports.
            </p>
          </div>
        ) : (
          <div className="space-y-1.5">
            {artifacts.map(({ name, versions }) => {
              const latestVersion = versions.length
                ? Math.max(...versions.map((v) => v.version))
                : undefined;
              const isSelected = selectedArtifact === name;

              return (
                <div
                  key={name}
                  className={clsx(
                    "border transition-colors",
                    isSelected
                      ? "border-primary bg-surface"
                      : "border-border bg-surface hover:border-primary/40"
                  )}
                >
                  <button
                    onClick={() =>
                      setSelectedArtifact(isSelected ? null : name)
                    }
                    className="w-full flex items-start gap-2 p-2 text-left"
                  >
                    {getIcon(name)}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-text-primary truncate">
                        {name}
                      </p>
                      <p className="text-[10px] text-text-muted mt-0.5">
                        {versions.length} version
                        {versions.length !== 1 ? "s" : ""}
                      </p>
                    </div>
                  </button>

                  {isSelected && sessionId && (
                    <div className="px-2 pb-2 space-y-1.5 border-t border-border pt-1.5">
                      {versions.map((v) => (
                        <div
                          key={v.version}
                          className="flex items-center justify-between text-xs"
                        >
                          <span className="text-text-muted">
                            v{v.version}
                          </span>
                          <a
                            href={getArtifactUrl(
                              userId,
                              sessionId,
                              name,
                              v.version
                            )}
                            download={name}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-primary hover:underline"
                          >
                            <Download className="w-3 h-3" strokeWidth={1.5} />
                            Download
                          </a>
                        </div>
                      ))}
                      {latestVersion !== undefined && (
                        <a
                          href={getArtifactUrl(
                            userId,
                            sessionId,
                            name,
                            latestVersion
                          )}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="md-btn-filled w-full text-[10px] py-1.5"
                        >
                          <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                          Open Latest
                        </a>
                      )}
                      <button
                        onClick={() => handleDelete(name)}
                        className="md-btn-outlined w-full text-[10px] py-1.5 text-danger border-danger/30"
                      >
                        <Trash2 className="w-3 h-3" strokeWidth={1.5} />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
}
