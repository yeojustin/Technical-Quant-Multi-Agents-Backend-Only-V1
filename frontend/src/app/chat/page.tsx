"use client";

import { useState, useCallback, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import AppShell from "@/components/AppShell";
import ChatInterface from "@/components/ChatInterface";
import ArtifactPanel from "@/components/ArtifactPanel";

function ChatPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showArtifacts, setShowArtifacts] = useState(true);
  const [artifactRefresh, setArtifactRefresh] = useState(0);

  const handleNewChat = useCallback(() => {
    setSessionId(null);
    router.push("/chat");
  }, [router]);

  const handleArtifactsUpdated = useCallback(() => {
    setArtifactRefresh((n) => n + 1);
  }, []);

  return (
    <AppShell
      onNewChat={handleNewChat}
      rightPanel={
        showArtifacts ? (
          <ArtifactPanel
            sessionId={sessionId}
            refreshTrigger={artifactRefresh}
            onClose={() => setShowArtifacts(false)}
          />
        ) : undefined
      }
    >
      <ChatInterface
        sessionId={sessionId}
        initialQuery={initialQuery}
        onSessionCreated={setSessionId}
        onArtifactsUpdated={handleArtifactsUpdated}
        showArtifactToggle={!showArtifacts}
        onToggleArtifacts={() => setShowArtifacts(true)}
      />
    </AppShell>
  );
}

export default function ChatPage() {
  return (
    <Suspense>
      <ChatPageContent />
    </Suspense>
  );
}
