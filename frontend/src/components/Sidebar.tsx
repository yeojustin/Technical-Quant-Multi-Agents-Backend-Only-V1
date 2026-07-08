"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  MessageSquare,
  FileBox,
  Plus,
  Menu,
  Key,
} from "lucide-react";
import clsx from "clsx";
import { useEffect, useState } from "react";
import ApiKeySettings from "./ApiKeySettings";
import { getStoredApiKey, maskApiKey } from "@/lib/api-key";

const NAV_ITEMS = [
  { href: "/", label: "Home", icon: Home },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/artifacts", label: "Exports", icon: FileBox },
];

interface SidebarProps {
  onNewChat?: () => void;
}

export default function Sidebar({ onNewChat }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [keyHint, setKeyHint] = useState<string | null>(null);

  const hasKey = Boolean(keyHint);

  const refreshKeyHint = () => {
    const key = getStoredApiKey();
    setKeyHint(key ? maskApiKey(key) : null);
  };

  useEffect(() => {
    refreshKeyHint();
  }, []);

  return (
    <aside
      className={clsx(
        "flex flex-col h-full bg-bg-sidebar border-r border-[var(--sidebar-border)] shrink-0 transition-[width] duration-150",
        collapsed ? "w-11" : "w-48"
      )}
    >
      <div className="flex items-center justify-between h-11 px-2 border-b border-[var(--sidebar-border)]">
        {!collapsed && (
          <Link href="/" className="px-2 min-w-0">
            <span className="text-xs font-semibold text-[var(--sidebar-text-active)] tracking-[-0.02em]">
              Quant
            </span>
          </Link>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 text-[var(--sidebar-text)] hover:text-[var(--sidebar-text-hover)]"
          aria-label={collapsed ? "Expand" : "Collapse"}
        >
          <Menu className="w-4 h-4" strokeWidth={1.5} />
        </button>
      </div>

      <div className="p-2">
        <button
          onClick={onNewChat}
          className={clsx(
            "w-full flex items-center justify-center gap-1.5 py-2 text-xs font-medium",
            "bg-[var(--sidebar-text-active)] text-[var(--sidebar-bg)] rounded-[var(--radius)]",
            "hover:bg-[#e5e5e5] transition-colors",
            collapsed && "px-0"
          )}
        >
          <Plus className="w-3.5 h-3.5" strokeWidth={2} />
          {!collapsed && "New"}
        </button>
      </div>

      <nav className="flex-1 px-2 space-y-px">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "md-nav-item",
                active && "md-nav-item-active",
                collapsed && "justify-center px-0"
              )}
              title={collapsed ? label : undefined}
            >
              <Icon className="w-4 h-4 shrink-0" strokeWidth={1.5} />
              {!collapsed && label}
            </Link>
          );
        })}
      </nav>

      <div className="p-2 border-t border-[var(--sidebar-border)]">
        <button
          onClick={() => setSettingsOpen(true)}
          className={clsx(
            "md-api-key-btn",
            hasKey ? "md-api-key-btn--set" : "md-api-key-btn--missing",
            collapsed && "justify-center px-1"
          )}
          title={collapsed ? "API Key" : undefined}
        >
          <Key className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
          {!collapsed && (
            <div className="text-left min-w-0 flex-1">
              <p className="text-xs font-medium leading-tight">
                {hasKey ? "API key" : "Set API key"}
              </p>
              <p className="text-[10px] opacity-70 truncate font-mono">
                {hasKey ? keyHint : "gemini · required"}
              </p>
            </div>
          )}
        </button>
      </div>

      <ApiKeySettings
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onSaved={refreshKeyHint}
      />
    </aside>
  );
}
