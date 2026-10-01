'use client';

import React from 'react';

interface HeaderProps {
  sessionId: string;
  onNewSession: () => void;
  isLoadingSession?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  sessionId,
  onNewSession,
  isLoadingSession = false,
}) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6">
        {/* Brand & Product Identity */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 via-indigo-600 to-cyan-400 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-slate-950">
              <span className="font-mono text-base font-black text-cyan-400">AX</span>
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-white sm:text-lg">
                AURONIX
              </h1>
              <span className="rounded-md bg-cyan-950/80 border border-cyan-800/60 px-2 py-0.5 font-mono text-[10px] font-semibold text-cyan-300">
                AI WORKBENCH
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Private Enterprise Operations & Incident Runbook Intelligence
            </p>
          </div>
        </div>

        {/* System & Session Indicators */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Grounding Status Pill */}
          <div className="hidden sm:flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/30 px-3 py-1 text-xs text-emerald-300">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            <span className="font-medium">RAG Grounding Active</span>
          </div>

          {/* Active Session Display */}
          <div className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs">
            <span className="text-slate-400 font-medium">Session:</span>
            <span className="font-mono text-cyan-300 max-w-[120px] truncate sm:max-w-none">
              {sessionId ? `${sessionId.slice(0, 8)}...` : 'Connecting...'}
            </span>
            <button
              type="button"
              onClick={onNewSession}
              disabled={isLoadingSession}
              title="Initialize a new isolated session (POST /sessions)"
              className="ml-1 rounded bg-slate-800 px-2 py-0.5 font-sans text-[11px] font-medium text-slate-300 hover:bg-cyan-600 hover:text-white transition disabled:opacity-50"
            >
              {isLoadingSession ? 'Resetting...' : 'New Session'}
            </button>
          </div>

          {/* Enterprise Badge */}
          <div className="hidden md:block rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1 font-mono text-[10px] text-slate-400">
            CONFIDENTIAL // INTERNAL
          </div>
        </div>
      </div>
    </header>
  );
};
