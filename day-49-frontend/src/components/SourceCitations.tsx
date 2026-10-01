'use client';

import React, { useState } from 'react';
import { Citation } from '@/types/auronix';

interface SourceCitationsProps {
  citations: Citation[];
}

export const SourceCitations: React.FC<SourceCitationsProps> = ({ citations }) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(true);

  if (!citations || citations.length === 0) {
    return (
      <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <svg className="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-medium text-slate-300">No external source citations referenced.</span>
        </div>
        <p className="mt-1 text-slate-400">
          This response was generated from base system parameters without external document retrieval.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-6 rounded-xl border border-indigo-500/30 bg-indigo-950/20 shadow-md transition-all">
      {/* Accordion Toggle Header */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-controls="citation-panel"
        className="flex w-full items-center justify-between px-5 py-3.5 text-left text-xs font-medium text-indigo-200 hover:bg-indigo-900/30 rounded-xl transition focus:outline-none focus:ring-2 focus:ring-indigo-400"
      >
        <div className="flex items-center gap-2.5">
          <svg className="h-4 w-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <span className="font-semibold tracking-wide text-indigo-100">
            Verified Source Citations ({citations.length} Documents Cited)
          </span>
          <span className="rounded bg-indigo-900/70 px-2 py-0.5 font-mono text-[11px] text-indigo-300">
            Grounding Evidence
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-indigo-300">
          <span>{isExpanded ? 'Collapse' : 'Expand'}</span>
          <svg
            className={`h-4 w-4 transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Citations Content */}
      {isExpanded && (
        <div id="citation-panel" className="space-y-3 px-5 pb-5 pt-1 border-t border-indigo-900/40">
          {citations.map((cite, index) => {
            const pct = Math.round(cite.similarityScore * 1000) / 10;
            return (
              <div
                key={index}
                className="rounded-lg border border-slate-800 bg-slate-900/70 p-3.5 text-xs transition hover:border-indigo-500/40"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="flex h-5 w-5 items-center justify-center rounded bg-indigo-900/60 font-mono text-[10px] font-bold text-indigo-300">
                      #{index + 1}
                    </span>
                    <span className="font-mono font-medium text-slate-200">
                      {cite.documentName}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] text-slate-400">Similarity:</span>
                    <span
                      className={`rounded px-2 py-0.5 font-mono text-[11px] font-bold ${
                        cite.similarityScore >= 0.95
                          ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/50'
                          : 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/50'
                      }`}
                    >
                      {cite.similarityScore.toFixed(3)} ({pct}%)
                    </span>
                  </div>
                </div>

                <div className="mt-2.5 rounded bg-black/40 p-2.5 font-sans leading-relaxed text-slate-300 border-l-2 border-indigo-400">
                  <span className="font-semibold text-indigo-300">Excerpt: </span>
                  {cite.excerpt}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
