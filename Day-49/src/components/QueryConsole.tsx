'use client';

import React, { useState, KeyboardEvent } from 'react';

interface QueryConsoleProps {
  query: string;
  onQueryChange: (val: string) => void;
  onSubmit: (testError?: string) => void;
  onClear: () => void;
  isStreaming: boolean;
  isPreparing: boolean;
}

export const QueryConsole: React.FC<QueryConsoleProps> = ({
  query,
  onQueryChange,
  onSubmit,
  onClear,
  isStreaming,
  isPreparing,
}) => {
  const [selectedDomain, setSelectedDomain] = useState<string>('All Domains');
  const [showErrorTester, setShowErrorTester] = useState<boolean>(false);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!isStreaming && !isPreparing) {
        onSubmit();
      }
    }
  };

  const domains = [
    'All Domains',
    'Incident Runbooks (P0/P1)',
    'System Architecture',
    'Security & Secrets',
    'Compliance & Governance',
  ];

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl backdrop-blur-md">
      {/* Domain Context Pills */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3 mb-4">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] font-mono text-slate-400 mr-1">Domain:</span>
          {domains.map((dom) => (
            <button
              key={dom}
              type="button"
              onClick={() => setSelectedDomain(dom)}
              className={`rounded-full px-2.5 py-1 text-xs font-medium transition ${
                selectedDomain === dom
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {dom}
            </button>
          ))}
        </div>

        {/* Toggle Error Simulation Bar */}
        <button
          type="button"
          onClick={() => setShowErrorTester(!showErrorTester)}
          className="text-xs text-slate-400 hover:text-cyan-300 font-mono underline decoration-dotted transition"
        >
          {showErrorTester ? 'Hide Error Testing Suite' : 'Test Day-45 Error Codes'}
        </button>
      </div>

      {/* Interactive Day-45 Error Code Testing Suite */}
      {showErrorTester && (
        <div className="mb-4 rounded-xl border border-amber-500/30 bg-amber-950/20 p-3 text-xs text-amber-200">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-amber-300">
              Interactive Day-45 API Error Verification Suite:
            </span>
            <span className="text-[11px] text-amber-400/80">
              Click any code to trigger its dedicated named error component
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => onSubmit('400')}
              className="rounded bg-amber-900/80 hover:bg-amber-800 px-2.5 py-1 font-mono text-[11px] text-amber-200 border border-amber-700/50"
            >
              HTTP 400 (InvalidInputError)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('401_missing')}
              className="rounded bg-red-900/80 hover:bg-red-800 px-2.5 py-1 font-mono text-[11px] text-red-200 border border-red-700/50"
            >
              HTTP 401 (Missing Key)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('401_invalid')}
              className="rounded bg-red-900/80 hover:bg-red-800 px-2.5 py-1 font-mono text-[11px] text-red-200 border border-red-700/50"
            >
              HTTP 401 (Invalid Key)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('404')}
              className="rounded bg-blue-900/80 hover:bg-blue-800 px-2.5 py-1 font-mono text-[11px] text-blue-200 border border-blue-700/50"
            >
              HTTP 404 (SessionNotFoundError)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('422')}
              className="rounded bg-purple-900/80 hover:bg-purple-800 px-2.5 py-1 font-mono text-[11px] text-purple-200 border border-purple-700/50"
            >
              HTTP 422 (ValidationError)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('429')}
              className="rounded bg-orange-900/80 hover:bg-orange-800 px-2.5 py-1 font-mono text-[11px] text-orange-200 border border-orange-700/50"
            >
              HTTP 429 (RateLimitError)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('500')}
              className="rounded bg-rose-900/80 hover:bg-rose-800 px-2.5 py-1 font-mono text-[11px] text-rose-200 border border-rose-700/50"
            >
              HTTP 500 (InternalServerError)
            </button>
            <button
              type="button"
              onClick={() => onSubmit('503')}
              className="rounded bg-red-950 hover:bg-red-900 px-2.5 py-1 font-mono text-[11px] text-red-300 border border-red-800/50"
            >
              HTTP 503 (ServiceUnavailable)
            </button>
          </div>
        </div>
      )}

      {/* Query Input Area */}
      <div className="relative">
        <label htmlFor="auronix-query-input" className="sr-only">
          Enter operational or technical question
        </label>
        <textarea
          id="auronix-query-input"
          rows={3}
          value={query}
          maxLength={1000}
          disabled={isStreaming || isPreparing}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask an internal operations, incident protocol, architecture, or policy question... (e.g. What is the database failover protocol for P0 outages?)"
          className="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 disabled:opacity-50 resize-y"
        />

        <div className="mt-2 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <kbd className="hidden sm:inline-block rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-slate-300 border border-slate-700">
              Ctrl + Enter
            </kbd>
            <span className="hidden sm:inline">to submit inquiry</span>
          </div>

          <div className="flex items-center gap-3">
            <span className="font-mono text-[11px] text-slate-500">
              {query.length} / 1000 characters
            </span>

            {query.length > 0 && !isStreaming && !isPreparing && (
              <button
                type="button"
                onClick={onClear}
                className="text-slate-400 hover:text-slate-200 transition underline"
              >
                Clear
              </button>
            )}

            <button
              type="button"
              disabled={isStreaming || isPreparing}
              onClick={() => onSubmit()}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 px-5 py-2 text-xs font-semibold text-white shadow-lg shadow-cyan-600/20 transition focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPreparing ? (
                <>
                  <svg className="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Grounding...</span>
                </>
              ) : isStreaming ? (
                <>
                  <span className="h-2 w-2 rounded-full bg-cyan-300 animate-ping" />
                  <span>Streaming Tokens...</span>
                </>
              ) : (
                <>
                  <svg className="h-4 w-4 text-cyan-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span>Submit Inquiry</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
