import { APP_NAME } from "./constants";
import { API_KEY_HEADER, getStoredApiKey } from "./api-key";
import type { AdkEvent, AdkSession, ArtifactVersion } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_ADK_API_URL || "/api/adk";

function withByokHeaders(headers?: HeadersInit): HeadersInit {
  const key = getStoredApiKey();
  if (!key) return headers ?? {};
  return { ...Object(headers ?? {}), [API_KEY_HEADER]: key };
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...withByokHeaders(options?.headers),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`ADK API error (${res.status}): ${text}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function listApps(): Promise<string[]> {
  return request<string[]>("/list-apps");
}

export async function createSession(
  userId: string,
  sessionId?: string,
  state?: Record<string, unknown>
): Promise<AdkSession> {
  const path = sessionId
    ? `/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}`
    : `/apps/${APP_NAME}/users/${userId}/sessions`;

  return request<AdkSession>(path, {
    method: "POST",
    body: JSON.stringify(state ?? {}),
  });
}

export async function getSession(
  userId: string,
  sessionId: string
): Promise<AdkSession> {
  return request<AdkSession>(
    `/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}`
  );
}

export async function listSessions(userId: string): Promise<AdkSession[]> {
  return request<AdkSession[]>(
    `/apps/${APP_NAME}/users/${userId}/sessions`
  );
}

export async function deleteSession(
  userId: string,
  sessionId: string
): Promise<void> {
  await request<void>(
    `/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}`,
    { method: "DELETE" }
  );
}

export async function runAgent(
  userId: string,
  sessionId: string,
  message: string
): Promise<AdkEvent[]> {
  return request<AdkEvent[]>("/run", {
    method: "POST",
    body: JSON.stringify({
      appName: APP_NAME,
      userId,
      sessionId,
      newMessage: {
        role: "user",
        parts: [{ text: message }],
      },
    }),
  });
}

export async function* streamAgent(
  userId: string,
  sessionId: string,
  message: string,
  streaming = true
): AsyncGenerator<AdkEvent> {
  const res = await fetch(`${API_BASE}/run_sse`, {
    method: "POST",
    headers: withByokHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      appName: APP_NAME,
      userId,
      sessionId,
      newMessage: {
        role: "user",
        parts: [{ text: message }],
      },
      streaming,
    }),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`ADK SSE error (${res.status}): ${text}`);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6).trim();
        if (data && data !== "[DONE]") {
          try {
            yield JSON.parse(data) as AdkEvent;
          } catch {
            // skip malformed SSE chunks
          }
        }
      }
    }
  }
}

export async function listArtifacts(
  userId: string,
  sessionId: string
): Promise<string[]> {
  return request<string[]>(
    `/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}/artifacts`
  );
}

export async function listArtifactVersions(
  userId: string,
  sessionId: string,
  artifactName: string
): Promise<ArtifactVersion[]> {
  return request<ArtifactVersion[]>(
    `/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}/artifacts/${encodeURIComponent(artifactName)}/versions`
  );
}

export function getArtifactUrl(
  userId: string,
  sessionId: string,
  artifactName: string,
  version?: number
): string {
  const base = `${API_BASE}/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}/artifacts/${encodeURIComponent(artifactName)}`;
  return version !== undefined ? `${base}/versions/${version}` : base;
}

export async function deleteArtifact(
  userId: string,
  sessionId: string,
  artifactName: string
): Promise<void> {
  await request<void>(
    `/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}/artifacts/${encodeURIComponent(artifactName)}`,
    { method: "DELETE" }
  );
}

export function extractTextFromEvents(events: AdkEvent[]): string {
  const texts: string[] = [];
  for (const event of events) {
    if (event.content?.role === "model" && event.content.parts) {
      for (const part of event.content.parts) {
        if (part.text) texts.push(part.text);
      }
    }
  }
  return texts.join("\n");
}

export function extractArtifactDeltas(events: AdkEvent[]): string[] {
  const artifacts = new Set<string>();
  for (const event of events) {
    const delta = event.actions?.artifactDelta;
    if (delta) {
      Object.keys(delta).forEach((k) => artifacts.add(k));
    }
  }
  return Array.from(artifacts);
}
