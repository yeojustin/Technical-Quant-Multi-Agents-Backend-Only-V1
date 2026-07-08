"use client";

import Sidebar from "./Sidebar";

interface AppShellProps {
  children: React.ReactNode;
  onNewChat?: () => void;
  rightPanel?: React.ReactNode;
}

export default function AppShell({
  children,
  onNewChat,
  rightPanel,
}: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar onNewChat={onNewChat} />
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {children}
      </main>
      {rightPanel}
    </div>
  );
}
