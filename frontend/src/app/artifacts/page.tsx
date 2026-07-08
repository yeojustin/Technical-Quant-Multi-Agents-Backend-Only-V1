"use client";

import { useEffect, useState, useCallback } from "react";
import {
  FileText,
  FileSpreadsheet,
  Download,
  Trash2,
  RefreshCw,
  FolderOpen,
  AlertCircle,
  ExternalLink,
} from "lucide-react";
import clsx from "clsx";
import AppShell from "@/components/AppShell";
import {
  listSessions,
  listArtifacts,
  listArtifactVersions,
  getArtifactUrl,
  deleteArtifact,
  deleteSession,
} from "@/lib/adk-api";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { ArtifactVersion } from "@/lib/types";

interface SessionArtifacts {
  sessionId: string;
  lastUpdate: number;
  artifacts: {
    name: string;
    versions: ArtifactVersion[];
  }[];
}

export default function ArtifactsPage() {
  const [sessions, setSessions] = useState<SessionArtifacts[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const sessionList = await listSessions(DEFAULT_USER_ID);
      const withArtifacts: SessionArtifacts[] = [];

      for (const session of sessionList) {
        try {
          const names = await listArtifacts(DEFAULT_USER_ID, session.id);
          if (names.length === 0) continue;

          const artifacts = await Promise.all(
            names.map(async (name) => {
              try {
                const versions = await listArtifactVersions(
                  DEFAULT_USER_ID,
                  session.id,
                  name
                );
                return { name, versions };
              } catch {
                return { name, versions: [] };
              }
            })
          );

          withArtifacts.push({
            sessionId: session.id,
            lastUpdate: session.lastUpdateTime,
            artifacts,
          });
        } catch {
          // skip sessions without artifacts
        }
      }

      withArtifacts.sort((a, b) => b.lastUpdate - a.lastUpdate);
      setSessions(withArtifacts);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load artifacts. Is the ADK backend running?"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleDeleteArtifact = async (
    sessionId: string,
    name: string
  ) => {
    if (!confirm(`Delete "${name}"?`)) return;
    try {
      await deleteArtifact(DEFAULT_USER_ID, sessionId, name);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm(`Delete session and all its artifacts?`)) return;
    try {
      await deleteSession(DEFAULT_USER_ID, sessionId);
      await loadAll();
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

  const formatDate = (ts: number) => {
    return new Date(ts * 1000).toLocaleString();
  };

  const totalArtifacts = sessions.reduce(
    (sum, s) => sum + s.artifacts.length,
    0
  );

  return (
    <AppShell>
      <div className="flex flex-col h-full bg-bg-primary">
        <header className="md-app-bar px-6 h-11 flex items-center shrink-0">
          <div className="flex items-center justify-between w-full max-w-3xl mx-auto">
            <div>
              <h1 className="text-sm font-medium text-text-primary tracking-[-0.01em]">
                Exports
              </h1>
              <p className="font-mono text-[10px] text-text-muted">
                pdf · xlsx
              </p>
            </div>
            <button
              onClick={loadAll}
              disabled={loading}
              className="md-btn-text text-xs disabled:opacity-50"
            >
              <RefreshCw
                className={clsx("w-3.5 h-3.5", loading && "animate-spin")}
                strokeWidth={1.5}
              />
              Refresh
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-8">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-8 mb-8 font-mono text-xs text-text-muted">
              <span>
                <span className="text-text-primary text-sm font-sans font-medium">{sessions.length}</span> sessions
              </span>
              <span>
                <span className="text-text-primary text-sm font-sans font-medium">{totalArtifacts}</span> files
              </span>
            </div>

            {error && (
              <div className="flex items-center gap-2 border border-danger/30 bg-surface px-3 py-2 mb-4 text-xs">
                <AlertCircle className="w-3.5 h-3.5 text-danger shrink-0" strokeWidth={1.5} />
                <p className="text-danger">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="w-5 h-5 text-text-muted animate-spin mx-auto mb-2" strokeWidth={1.5} />
                <p className="text-xs text-text-muted">Loading...</p>
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center py-12 border border-dashed border-border bg-surface px-4">
                <FolderOpen className="w-6 h-6 flat-icon mx-auto mb-2" strokeWidth={1.5} />
                <h3 className="text-sm font-medium text-text-primary mb-1">
                  No artifacts yet
                </h3>
                <p className="text-xs text-text-muted max-w-sm mx-auto">
                  Run an analysis in chat to generate PDF and Excel exports.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {sessions.map((session) => {
                  const isExpanded = expandedSession === session.sessionId;
                  return (
                    <div
                      key={session.sessionId}
                      className="md-card overflow-hidden"
                    >
                      <button
                        onClick={() =>
                          setExpandedSession(
                            isExpanded ? null : session.sessionId
                          )
                        }
                        className="w-full flex items-center justify-between p-3 hover:bg-bg-secondary transition-colors text-left"
                      >
                        <div className="min-w-0">
                          <p className="text-xs font-medium text-text-primary truncate">
                            {session.sessionId.slice(0, 20)}…
                          </p>
                          <p className="text-[10px] text-text-muted mt-0.5">
                            {session.artifacts.length} file
                            {session.artifacts.length !== 1 ? "s" : ""} ·{" "}
                            {formatDate(session.lastUpdate)}
                          </p>
                        </div>
                        <span className="text-[10px] text-text-muted shrink-0 ml-2">
                          {isExpanded ? "−" : "+"}
                        </span>
                      </button>

                      {isExpanded && (
                        <div className="border-t border-border p-2 space-y-1.5 bg-bg-primary">
                          {session.artifacts.map(({ name, versions }) => {
                            const latest = versions.length
                              ? Math.max(...versions.map((v) => v.version))
                              : undefined;
                            return (
                              <div
                                key={name}
                                className="flex items-center gap-2 p-2 bg-surface border border-border"
                              >
                                {getIcon(name)}
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-medium text-text-primary truncate">
                                    {name}
                                  </p>
                                  <p className="text-[10px] text-text-muted">
                                    {versions.length} v
                                    {versions.length !== 1 ? "s" : ""}
                                  </p>
                                </div>
                                <div className="flex items-center gap-0.5 shrink-0">
                                  {latest !== undefined && (
                                    <>
                                      <a
                                        href={getArtifactUrl(
                                          DEFAULT_USER_ID,
                                          session.sessionId,
                                          name,
                                          latest
                                        )}
                                        download={name}
                                        className="p-1.5 hover:bg-bg-secondary text-text-muted hover:text-primary"
                                        title="Download"
                                      >
                                        <Download className="w-3.5 h-3.5" strokeWidth={1.5} />
                                      </a>
                                      <a
                                        href={getArtifactUrl(
                                          DEFAULT_USER_ID,
                                          session.sessionId,
                                          name,
                                          latest
                                        )}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="p-1.5 hover:bg-bg-secondary text-text-muted hover:text-primary"
                                        title="Open"
                                      >
                                        <ExternalLink className="w-3.5 h-3.5" strokeWidth={1.5} />
                                      </a>
                                    </>
                                  )}
                                  <button
                                    onClick={() =>
                                      handleDeleteArtifact(
                                        session.sessionId,
                                        name
                                      )
                                    }
                                    className="p-1.5 hover:bg-bg-secondary text-text-muted hover:text-danger"
                                    title="Delete"
                                  >
                                    <Trash2 className="w-3.5 h-3.5" strokeWidth={1.5} />
                                  </button>
                                </div>
                              </div>
                            );
                          })}
                          <button
                            onClick={() =>
                              handleDeleteSession(session.sessionId)
                            }
                            className="md-btn-text text-xs text-danger normal-case"
                          >
                            Delete entire session
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
