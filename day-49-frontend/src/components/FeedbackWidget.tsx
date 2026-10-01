'use client';

import React, { useState } from 'react';
import { FeedbackResponse } from '@/types/auronix';

interface FeedbackWidgetProps {
  sessionId: string;
  queryReference?: string;
  apiKey?: string;
}

export const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  sessionId,
  queryReference,
  apiKey = 'auronix-secret-key-45',
}) => {
  const [rating, setRating] = useState<'positive' | 'negative' | null>(null);
  const [feedbackType, setFeedbackType] = useState<
    'grounding_accuracy' | 'relevance' | 'hallucination_report' | 'general'
  >('grounding_accuracy');
  const [comment, setComment] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submittedData, setSubmittedData] = useState<FeedbackResponse | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  const handleSubmit = async (selectedRating?: 'positive' | 'negative') => {
    const activeRating = selectedRating || rating;
    if (!activeRating) return;

    setIsSubmitting(true);
    setFeedbackError(null);

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
        },
        body: JSON.stringify({
          session_id: sessionId,
          query_reference: queryReference || 'AURONIX operational query',
          feedback_type: feedbackType,
          rating: activeRating,
          comment: comment.trim() || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || 'Failed to submit feedback.');
      }

      setSubmittedData(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Network error while recording feedback.';
      setFeedbackError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickThumb = (type: 'positive' | 'negative') => {
    setRating(type);
    handleSubmit(type);
  };

  // State: Successfully submitted feedback (prevents accidental duplicate submissions)
  if (submittedData) {
    return (
      <div className="mt-5 rounded-xl border border-emerald-500/40 bg-emerald-950/20 p-4 text-xs text-emerald-200">
        <div className="flex items-center gap-2">
          <svg className="h-4 w-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span className="font-semibold text-emerald-100">
            {submittedData.message} (Feedback #{submittedData.feedback_id})
          </span>
        </div>
        <p className="mt-1 text-emerald-300/80">
          Thank you. Your grounding telemetry has been recorded to SQLite store for audit & model refinement.
        </p>
      </div>
    );
  }

  return (
    <div className="mt-5 rounded-xl border border-slate-800 bg-slate-900/60 p-4 transition-all">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-300">
          <svg className="h-4 w-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Was this operational response grounded & accurate?</span>
        </div>

        {/* Thumbs Up / Down Controls */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleQuickThumb('positive')}
            aria-label="Thumbs up: Grounded and helpful response"
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
              rating === 'positive'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-emerald-300'
            }`}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
            </svg>
            <span>Accurate</span>
          </button>

          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => setRating('negative')}
            aria-label="Thumbs down: Flag hallucination or inaccurate response"
            className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition ${
              rating === 'negative'
                ? 'bg-rose-600 text-white shadow-md'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-rose-300'
            }`}
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76 1.34m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
            </svg>
            <span>Hallucination / Issue</span>
          </button>
        </div>
      </div>

      {/* Expanded detail box if negative rating or user wants to add notes */}
      {rating && (
        <div className="mt-4 pt-3 border-t border-slate-800 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label htmlFor="feedback-type" className="block text-slate-400 font-medium mb-1">
                Feedback Category:
              </label>
              <select
                id="feedback-type"
                value={feedbackType}
                onChange={(e) =>
                  setFeedbackType(
                    e.target.value as
                      | 'grounding_accuracy'
                      | 'relevance'
                      | 'hallucination_report'
                      | 'general'
                  )
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              >
                <option value="grounding_accuracy">Grounding Accuracy (Factual runbook check)</option>
                <option value="relevance">Relevance (Addressed operational task)</option>
                <option value="hallucination_report">Hallucination Report (Fabricated protocol)</option>
                <option value="general">General Quality / Formatting</option>
              </select>
            </div>

            <div>
              <label htmlFor="feedback-comment" className="block text-slate-400 font-medium mb-1">
                Comments (Optional, max 500 chars):
              </label>
              <input
                id="feedback-comment"
                type="text"
                maxLength={500}
                placeholder="e.g. Cited incorrect database port number..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={() => handleSubmit()}
              className="rounded-lg bg-cyan-600 hover:bg-cyan-500 px-3 py-1.5 text-xs font-semibold text-white shadow transition focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50"
            >
              {isSubmitting ? 'Recording...' : 'Submit Feedback to Day-45 Store'}
            </button>
          </div>
        </div>
      )}

      {feedbackError && (
        <div className="mt-2 text-xs text-rose-400 font-medium">
          Error: {feedbackError}
        </div>
      )}
    </div>
  );
};
