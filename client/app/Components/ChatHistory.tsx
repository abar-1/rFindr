"use client";

import React, { useEffect, useState } from "react";
import type { MatchResult } from "../contexts/MatchContext";

// Runtime-configurable API URL (matches AuthContext), localhost fallback.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// A row from chat_logs as returned by GET /rag/chats.
interface ChatLog {
  id: number;
  user_id: number;
  prompt: string;
  matched_professors: MatchResult[];
  timestamp?: string;
  created_at?: string;
}

function formatDate(iso?: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

interface ChatHistoryProps {
  open: boolean;
  onClose: () => void;
}

export default function ChatHistory({ open, onClose }: ChatHistoryProps) {
  const [chats, setChats] = useState<ChatLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  // Sidebar is expanded by default when the overlay opens.
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Fetch the logged-in user's chat history whenever the overlay is opened.
  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      setSelectedId(null);
      setSidebarOpen(true);
      try {
        const res = await fetch(`${API_URL}/api/rag/chats`, {
          credentials: "include",
        });
        if (!res.ok) throw new Error("Failed to load chat history.");
        const data: ChatLog[] = await res.json();
        if (cancelled) return;
        setChats(data);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Something went wrong.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open]);

  if (!open) return null;

  const selected = chats.find((c) => c.id === selectedId) ?? null;

  // ---- Responsive visibility rules ----
  // Sidebar: full width on mobile, 20% on laptop. On mobile it hides once a
  // chat is selected so the detail view takes over the screen.
  const sidebarClasses = [
    "flex flex-col bg-white border-r border-gray-200 overflow-hidden shrink-0 transition-[width] duration-300 ease-in-out",
    sidebarOpen ? "w-full lg:w-1/5" : "w-0",
    selected ? "hidden lg:flex" : "flex",
  ].join(" ");

  // Detail pane: on mobile it shows only when a chat is selected; on laptop
  // it's always present alongside the sidebar.
  const detailClasses = [
    "flex-1 flex-col overflow-hidden bg-gray-50",
    selected ? "flex" : "hidden lg:flex",
  ].join(" ");

  const ToggleButton = (
    <button
      type="button"
      onClick={() => setSidebarOpen((s) => !s)}
      aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
      className="rounded-lg p-2 text-gray-600 hover:bg-gray-100 transition-colors"
    >
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    </button>
  );

  return (
    <div className="fixed inset-0 z-50 flex bg-gray-50">
      {/* ---- Sidebar: list of past chats ---- */}
      <aside className={sidebarClasses}>
        <div className="flex items-center gap-2 px-3 py-3 border-b border-gray-200">
          {ToggleButton}
          <h2 className="text-lg font-bold text-indigo-700">Chat History</h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close chat history"
            className="ml-auto rounded-lg px-2 py-1 text-sm font-semibold text-gray-500 hover:bg-gray-100 transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <p className="px-4 py-6 text-sm text-gray-500">Loading…</p>
          ) : error ? (
            <p className="px-4 py-6 text-sm text-red-600">{error}</p>
          ) : chats.length === 0 ? (
            <p className="px-4 py-6 text-sm text-gray-500">No saved chats yet.</p>
          ) : (
            <ul className="py-2">
              {chats.map((chat) => {
                const active = chat.id === selectedId;
                return (
                  <li key={chat.id}>
                    <button
                      type="button"
                      onClick={() => setSelectedId(chat.id)}
                      className={`w-full text-left px-4 py-3 transition-colors ${
                        active
                          ? "bg-indigo-50 border-l-4 border-indigo-600"
                          : "border-l-4 border-transparent hover:bg-gray-50"
                      }`}
                    >
                      <p className="truncate font-medium text-gray-800">
                        {chat.prompt || "Untitled search"}
                      </p>
                      <p className="mt-0.5 text-xs text-gray-400">
                        {formatDate(chat.timestamp ?? chat.created_at)}
                        {chat.matched_professors?.length
                          ? ` · ${chat.matched_professors.length} matches`
                          : ""}
                      </p>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </aside>

      {/* ---- Detail pane ---- */}
      <div className={detailClasses}>
        {/* Top bar: toggle (top-left) on laptop; back button on mobile */}
        <div className="flex items-center gap-2 border-b border-gray-200 bg-white px-3 py-3">
          {/* Back to the list on mobile */}
          <button
            type="button"
            onClick={() => setSelectedId(null)}
            aria-label="Back to chat list"
            className="lg:hidden rounded-lg p-2 text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              <path d="M12 4l-6 6 6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>

          {/* Sidebar toggle stays top-left on laptop (visible when sidebar collapsed) */}
          <div className="hidden lg:block">{ToggleButton}</div>

          <h2 className="truncate font-semibold text-gray-700">
            {selected ? selected.prompt || "Search details" : "Chat History"}
          </h2>

          <button
            type="button"
            onClick={onClose}
            className="ml-auto hidden lg:block rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-600 hover:bg-gray-100 transition-colors"
          >
            Close ✕
          </button>
        </div>

        {/* Selected chat content */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          {selected ? (
            <div className="mx-auto max-w-3xl">
              <p className="text-xs uppercase tracking-wide text-gray-400">
                {formatDate(selected.timestamp ?? selected.created_at)}
              </p>
              <h1 className="mt-1 mb-1 text-2xl font-bold text-gray-800">Your search</h1>
              <p className="mb-8 rounded-xl bg-white p-4 text-gray-700 shadow-sm border border-gray-100">
                {selected.prompt}
              </p>

              <h2 className="mb-4 text-xl font-semibold text-indigo-700">
                Matches ({selected.matched_professors?.length ?? 0})
              </h2>

              {selected.matched_professors?.length ? (
                <ul className="space-y-4">
                  {selected.matched_professors.map((prof, i) => (
                    <li
                      key={prof.professor_id ?? i}
                      className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm hover:shadow-md transition-shadow"
                    >
                      <h3 className="text-lg font-semibold text-gray-800">{prof.name}</h3>
                      {prof.department && (
                        <p className="mt-1 text-sm text-gray-600">
                          <span className="font-medium">Department:</span> {prof.department}
                        </p>
                      )}
                      {prof.email && (
                        <p className="mt-0.5 text-sm text-gray-600">
                          <span className="font-medium">Email:</span> {prof.email}
                        </p>
                      )}
                      {typeof prof.similarity === "number" && (
                        <p className="mt-0.5 text-sm text-gray-600">
                          <span className="font-medium">Similarity:</span>{" "}
                          {(prof.similarity * 100).toFixed(2)}%
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No matches were saved with this search.</p>
              )}
            </div>
          ) : (
            <div className="flex h-full items-center justify-center">
              <p className="text-gray-500">
                {loading ? "Loading…" : "Select a chat to view its details."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
