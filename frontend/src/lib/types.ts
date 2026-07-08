export interface AdkSession {
  id: string;
  appName: string;
  userId: string;
  state: Record<string, unknown>;
  events: AdkEvent[];
  lastUpdateTime: number;
}

export interface AdkEvent {
  id: string;
  author: string;
  timestamp: number;
  invocationId?: string;
  content?: {
    role?: string;
    parts?: AdkPart[];
  };
  actions?: {
    stateDelta?: Record<string, unknown>;
    artifactDelta?: Record<string, number>;
  };
}

export interface AdkPart {
  text?: string;
  functionCall?: {
    id: string;
    name: string;
    args: Record<string, unknown>;
  };
  functionResponse?: {
    id: string;
    name: string;
    response: Record<string, unknown>;
  };
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  author?: string;
  timestamp: number;
  isStreaming?: boolean;
}

export interface ArtifactInfo {
  name: string;
  version?: number;
  mimeType?: string;
  size?: number;
}

export interface ArtifactVersion {
  version: number;
  mimeType?: string;
  createTime?: number;
}
