'use client';

import React from 'react';

interface StreamingIndicatorProps {
  tokenCount: number;
  content: string;
}

export const StreamingIndicator: React.FC<StreamingIndicatorProps> = ({
  tokenCount,
  content,
}) => {
  return (
    <div
      role="region"
      aria-live="polite"
      aria-label="Streaming AI response"
      className="rounded-2xl border border-cyan-500/50 bg-slate-900/80 p-6 shadow-2xl backdrop-blur-md transition-all"
    >
      {/* Streaming Header status */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="relative flex h-3.5 w-3.5 items-center justify-center">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-cyan-500" />
          </div>
          <span className="text-xs font-mono font-bold tracking-wider text-cyan-300">
            STATE 2: STREAMING ACTIVE — RECEIVING TOKENS VIA READABLESTREAM
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="rounded-md bg-cyan-950/80 border border-cyan-800/50 px-2.5 py-1 text-cyan-300">
            {tokenCount} tokens received
          </span>
          <span className="rounded-md bg-slate-800 px-2.5 py-1 text-slate-300">
            Fetch API + Stream
          </span>
        </div>
      </div>

      {/* Streaming Content Display with Typing Cursor */}
      <div className="mt-5 space-y-4 font-sans text-sm md:text-base leading-relaxed text-slate-100 whitespace-pre-wrap selection:bg-cyan-500 selection:text-black">
        {content}
        <span
          aria-hidden="true"
          className="inline-block h-5 w-2 translate-y-0.5 ml-1 bg-cyan-400 animate-pulse"
        />
      </div>

      {/* Footer Streaming Wave Bar */}
      <div className="mt-6 flex items-center justify-between rounded-lg bg-slate-950/60 border border-slate-800/80 px-4 py-2.5">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <svg className="h-4 w-4 animate-spin text-cyan-400" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span>Progressive chunk rendering in browser...</span>
        </div>
        <div className="flex gap-1">
          <span className="h-2 w-1 rounded bg-cyan-400 animate-bounce" style={{ animationDelay: '0ms' }} />
          <span className="h-3 w-1 rounded bg-cyan-400 animate-bounce" style={{ animationDelay: '150ms' }} />
          <span className="h-2 w-1 rounded bg-cyan-400 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
};
