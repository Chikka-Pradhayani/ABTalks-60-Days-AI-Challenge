'use client';

import React from 'react';

export const SkeletonLoader: React.FC = () => {
  return (
    <div
      role="status"
      aria-label="Preparing AI response"
      className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-6 shadow-xl backdrop-blur-md animate-pulse"
    >
      {/* Top telemetry skeleton */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="h-4 w-4 rounded-full bg-cyan-500/40 animate-ping" />
          <span className="text-xs font-mono text-cyan-400 font-semibold tracking-wide">
            STATE 1: SKELETON LOADER — PREPARING GROUNDED INFERENCE
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-6 w-20 rounded-md bg-slate-800" />
          <div className="h-6 w-24 rounded-md bg-slate-800" />
        </div>
      </div>

      {/* Progress sub-steps */}
      <div className="my-4 flex flex-wrap gap-2 text-xs">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-cyan-950/60 border border-cyan-800/40 px-3 py-1 text-cyan-300">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse" />
          Query Embeddings Generated
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-950/60 border border-indigo-800/40 px-3 py-1 text-indigo-300">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Searching Vector Runbooks
        </span>
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-950/60 border border-emerald-800/40 px-3 py-1 text-emerald-300">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Synthesizing Zero-Hallucination Grounding
        </span>
      </div>

      {/* Text skeleton lines */}
      <div className="space-y-3 pt-2">
        <div className="h-5 w-2/5 rounded bg-slate-700/80" />
        <div className="h-4 w-full rounded bg-slate-800/80" />
        <div className="h-4 w-11/12 rounded bg-slate-800/80" />
        <div className="h-4 w-4/5 rounded bg-slate-800/70" />
        <div className="h-4 w-5/6 rounded bg-slate-800/60" />
      </div>

      {/* Citations block skeleton */}
      <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/40 p-4">
        <div className="flex items-center justify-between">
          <div className="h-4 w-36 rounded bg-slate-700/60" />
          <div className="h-4 w-16 rounded bg-slate-800" />
        </div>
        <div className="mt-3 space-y-2">
          <div className="h-3 w-3/4 rounded bg-slate-800/70" />
          <div className="h-3 w-1/2 rounded bg-slate-800/50" />
        </div>
      </div>
    </div>
  );
};
