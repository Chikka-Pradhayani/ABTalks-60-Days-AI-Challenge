'use client';

import React from 'react';

interface RunbookPresetsProps {
  onSelectPreset: (query: string) => void;
  disabled?: boolean;
}

const PRESETS = [
  {
    category: 'Incident P0/P1',
    label: 'DB Failover Protocol',
    query: 'What is the immediate failover protocol when a P0 Aurora DB crash occurs?',
    badgeColor: 'border-rose-500/40 text-rose-300 bg-rose-950/30',
  },
  {
    category: 'Architecture',
    label: 'Microservice Ports & Envoy',
    query: 'What is the AURONIX microservice architecture and port allocation matrix?',
    badgeColor: 'border-indigo-500/40 text-indigo-300 bg-indigo-950/30',
  },
  {
    category: 'Security',
    label: 'API Key & Token Rotation',
    query: 'What is the enterprise policy and lifecycle for rotating API keys and Vault tokens?',
    badgeColor: 'border-cyan-500/40 text-cyan-300 bg-cyan-950/30',
  },
  {
    category: 'Governance',
    label: 'Zero-Hallucination Standard',
    query: 'How does AURONIX enforce zero-hallucination grounding in internal company files?',
    badgeColor: 'border-emerald-500/40 text-emerald-300 bg-emerald-950/30',
  },
];

export const RunbookPresets: React.FC<RunbookPresetsProps> = ({
  onSelectPreset,
  disabled = false,
}) => {
  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4">
      <div className="flex items-center justify-between mb-2.5">
        <span className="text-xs font-mono font-semibold uppercase tracking-wider text-slate-400">
          Quick Operational Presets
        </span>
        <span className="text-[11px] text-slate-500">
          Click to load verified runbook query
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {PRESETS.map((preset, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPreset(preset.query)}
            className="flex flex-col text-left rounded-lg border border-slate-800 bg-slate-900/80 p-3 transition hover:border-slate-600 hover:bg-slate-800/70 focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50"
          >
            <span className={`inline-block w-fit rounded border px-1.5 py-0.5 text-[10px] font-mono font-semibold ${preset.badgeColor}`}>
              {preset.category}
            </span>
            <span className="mt-1.5 text-xs font-medium text-slate-200">
              {preset.label}
            </span>
            <span className="mt-1 line-clamp-1 text-[11px] text-slate-400">
              {preset.query}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};
