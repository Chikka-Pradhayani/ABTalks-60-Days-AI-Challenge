'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Header } from '@/components/Header';
import { RunbookPresets } from '@/components/RunbookPresets';
import { QueryConsole } from '@/components/QueryConsole';
import { SkeletonLoader } from '@/components/SkeletonLoader';
import { StreamingIndicator } from '@/components/StreamingIndicator';
import { CompletionState } from '@/components/CompletionState';
import { AuronixErrorDispatcher } from '@/components/ErrorComponents';
import { useAuronixStream } from '@/hooks/useAuronixStream';

export default function AuronixWorkbenchPage() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isLoadingSession, setIsLoadingSession] = useState<boolean>(false);
  const [query, setQuery] = useState<string>('');
  const [lastSubmittedQuery, setLastSubmittedQuery] = useState<string>('');

  const {
    streamState,
    streamedContent,
    tokenCount,
    metadata,
    apiError,
    sendQuery,
    reset,
  } = useAuronixStream();

  // Initialize session on mount via POST /api/sessions (matching Day-45)
  const initSession = useCallback(async () => {
    setIsLoadingSession(true);
    try {
      const res = await fetch('/api/sessions', {
        method: 'POST',
        headers: {
          'x-api-key': 'auronix-secret-key-45',
        },
      });
      const data = await res.json();
      if (res.ok && data.success && data.session_id) {
        setSessionId(data.session_id);
      } else {
        // Fallback UUID if local route unavailable
        setSessionId('session-' + Math.random().toString(36).substring(2, 11));
      }
    } catch {
      setSessionId('session-' + Math.random().toString(36).substring(2, 11));
    } finally {
      setIsLoadingSession(false);
    }
  }, []);

  useEffect(() => {
    initSession();
  }, [initSession]);

  const handleSubmit = (testErrorHeader?: string) => {
    // If not testing a simulated error, require query text
    if (!testErrorHeader && (!query || !query.trim())) {
      // Trigger local 400 InvalidInputError
      sendQuery(sessionId, '   ');
      return;
    }

    const activeQuery = query.trim() || 'Simulated test query for error verification';
    setLastSubmittedQuery(activeQuery);

    sendQuery(sessionId, activeQuery, {
      testErrorHeader,
    });
  };

  const handleSelectPreset = (presetQuery: string) => {
    setQuery(presetQuery);
    setLastSubmittedQuery(presetQuery);
    sendQuery(sessionId, presetQuery);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation & Status Bar */}
      <Header
        sessionId={sessionId}
        onNewSession={initSession}
        isLoadingSession={isLoadingSession}
      />

      <main className="flex-1 mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        {/* Purpose-Built Product Hero Banner */}
        <section aria-labelledby="product-overview" className="rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 p-6 shadow-xl">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded bg-cyan-950 border border-cyan-800/80 px-2 py-0.5 font-mono text-[10px] font-bold text-cyan-300">
                  DAY 49 FRONTEND SPRINT
                </span>
                <span className="text-xs text-slate-400">
                  Zero-Hallucination Enterprise RAG Interface
                </span>
              </div>
              <h2 id="product-overview" className="mt-2 text-xl font-bold tracking-tight text-white sm:text-2xl">
                AURONIX Private Enterprise AI Workbench
              </h2>
              <p className="mt-1 max-w-3xl text-xs sm:text-sm text-slate-300 leading-relaxed">
                Purpose-built intelligence console for internal software engineers, SREs, and operations staff.
                Queries are strictly grounded in corporate runbooks, architecture topologies, and incident protocols with full citation provenance and live token streaming.
              </p>
            </div>

            {/* Quick Architecture Pill Tags */}
            <div className="flex flex-wrap lg:flex-col items-start gap-1.5 text-[11px] font-mono shrink-0">
              <span className="rounded bg-slate-800/90 px-2.5 py-1 text-slate-300 border border-slate-700/50">
                Next.js 14 + Tailwind CSS
              </span>
              <span className="rounded bg-slate-800/90 px-2.5 py-1 text-cyan-300 border border-cyan-800/40">
                ReadableStream Token Rendering
              </span>
              <span className="rounded bg-slate-800/90 px-2.5 py-1 text-emerald-300 border border-emerald-800/40">
                Day-45 Backend & Feedback Wire
              </span>
            </div>
          </div>
        </section>

        {/* Operational Presets */}
        <RunbookPresets
          onSelectPreset={handleSelectPreset}
          disabled={streamState === 'skeleton' || streamState === 'streaming'}
        />

        {/* Primary Query Console */}
        <QueryConsole
          query={query}
          onQueryChange={setQuery}
          onSubmit={handleSubmit}
          onClear={() => setQuery('')}
          isStreaming={streamState === 'streaming'}
          isPreparing={streamState === 'skeleton'}
        />

        {/* Dynamic AI Response & State Container */}
        <section aria-label="Operational AI Response Container" className="space-y-4">
          {/* State 1: Skeleton Loader */}
          {streamState === 'skeleton' && <SkeletonLoader />}

          {/* State 2: Typing / Streaming Indicator */}
          {streamState === 'streaming' && (
            <StreamingIndicator
              tokenCount={tokenCount}
              content={streamedContent}
            />
          )}

          {/* State 3: Completion State */}
          {streamState === 'completed' && (
            <CompletionState
              content={streamedContent}
              metadata={metadata}
              queryReference={lastSubmittedQuery}
              onNewQuery={() => setQuery('')}
            />
          )}

          {/* Named Error Components (State: Error) */}
          {streamState === 'error' && apiError && (
            <AuronixErrorDispatcher
              error={apiError}
              onRetry={() => handleSubmit()}
              onNewSession={initSession}
              onClearInput={() => setQuery('')}
              onDismiss={reset}
            />
          )}

          {/* Initial Clean Guide State (when idle and no response yet) */}
          {streamState === 'idle' && (
            <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/30 p-8 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-950/60 border border-cyan-800/40 text-cyan-400 mb-3">
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-sm font-semibold text-slate-200">
                Workbench Ready for Grounded Inquiry
              </h3>
              <p className="mt-1 max-w-md mx-auto text-xs text-slate-400">
                Select an operational runbook preset above or type a specific engineering query. Tokens will render progressively via <code className="text-cyan-300 font-mono">ReadableStream</code>.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-3 text-xs text-slate-500 font-mono">
                <span>• State 1: Skeleton Loader</span>
                <span>• State 2: Active Stream</span>
                <span>• State 3: Grounded Completion</span>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 flex flex-wrap items-center justify-between gap-2">
          <span>AURONIX Enterprise Private AI Workbench • Day 49 Implementation</span>
          <span className="font-mono text-[11px] text-slate-600">
            Next.js 14 App Router • Tailwind CSS • Accessible Semantic UI
          </span>
        </div>
      </footer>
    </div>
  );
}
