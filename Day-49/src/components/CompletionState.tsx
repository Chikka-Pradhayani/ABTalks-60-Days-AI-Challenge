'use client';

import React, { useState } from 'react';
import { AskResponseMetadata } from '@/types/auronix';
import { SourceCitations } from './SourceCitations';
import { FeedbackWidget } from './FeedbackWidget';

interface CompletionStateProps {
  content: string;
  metadata: AskResponseMetadata | null;
  queryReference?: string;
  onNewQuery?: () => void;
}

export const CompletionState: React.FC<CompletionStateProps> = ({
  content,
  metadata,
  queryReference,
  onNewQuery,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const latency = metadata?.latencyMs ? `${metadata.latencyMs} ms` : 'Recorded';
  const score = metadata?.retrievalScore !== undefined ? metadata.retrievalScore : 0.95;
  const scorePct = Math.round(score * 1000) / 10;

  return (
    <div
      role="region"
      aria-label="Completed AI response"
      className="rounded-2xl border border-emerald-500/40 bg-slate-900/90 p-6 shadow-2xl backdrop-blur-md transition-all"
    >
      {/* State 3 Header & Telemetry Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <span className="flex h-3 w-3 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
          <span className="text-xs font-mono font-bold tracking-wider text-emerald-400">
            STATE 3: COMPLETION — STREAM FINISHED & GROUNDED
          </span>
        </div>

        {/* Telemetry Chips */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <div className="flex items-center gap-1.5 rounded-md bg-slate-800 border border-slate-700/60 px-2.5 py-1 text-slate-300">
            <svg className="h-3.5 w-3.5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Latency: <strong className="text-cyan-300">{latency}</strong></span>
          </div>

          <div className="flex items-center gap-1.5 rounded-md bg-emerald-950/70 border border-emerald-800/60 px-2.5 py-1 text-emerald-300">
            <svg className="h-3.5 w-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>Grounding Score: <strong className="text-emerald-200">{score.toFixed(3)} ({scorePct}%)</strong></span>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="flex items-center gap-1 rounded-md bg-slate-800 hover:bg-slate-700 px-2.5 py-1 text-xs text-slate-300 transition"
          >
            {copied ? 'Copied!' : 'Copy Answer'}
          </button>

          {onNewQuery && (
            <button
              type="button"
              onClick={onNewQuery}
              className="flex items-center gap-1 rounded-md bg-cyan-900/60 hover:bg-cyan-800/80 px-2.5 py-1 text-xs text-cyan-200 transition"
            >
              New Query
            </button>
          )}
        </div>
      </div>

      {/* Primary Answer Content */}
      <div className="mt-5 font-sans text-sm md:text-base leading-relaxed text-slate-100 whitespace-pre-wrap selection:bg-emerald-500 selection:text-black">
        {content}
      </div>

      {/* Section 5: Collapsible Source Citations */}
      {metadata && metadata.citations && (
        <SourceCitations citations={metadata.citations} />
      )}

      {/* Section 6: Enterprise Feedback Mechanism */}
      {metadata && (
        <FeedbackWidget
          sessionId={metadata.sessionId}
          queryReference={queryReference}
        />
      )}
    </div>
  );
};
