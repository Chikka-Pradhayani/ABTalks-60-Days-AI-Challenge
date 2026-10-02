'use client';

import React from 'react';
import { ApiErrorDetail } from '@/types/auronix';

interface ErrorComponentProps {
  rawError?: string;
  onRetry?: () => void;
  onNewSession?: () => void;
  onClearInput?: () => void;
  onDismiss?: () => void;
}

/**
 * HTTP 400 Bad Request — Named Component for Whitespace/Empty Input
 */
export const InvalidInputError: React.FC<ErrorComponentProps> = ({
  rawError,
  onClearInput,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-amber-500/40 bg-amber-950/20 p-5 text-amber-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-amber-300">
              Invalid Input Error (HTTP 400)
            </h4>
            <span className="rounded bg-amber-900/60 px-2 py-0.5 text-xs font-mono text-amber-300">
              INVALID_INPUT
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-amber-100">
            The submitted query cannot be empty or contain only blank spaces.
          </p>
          <p className="mt-1 text-xs text-amber-300/80">
            Suggested Action: Please type a descriptive question about internal architecture, incident runbooks, or corporate policies.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-amber-400/90">
              Server diagnostic: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onClearInput && (
              <button
                type="button"
                onClick={onClearInput}
                className="rounded-lg bg-amber-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-400"
              >
                Clear & Re-enter Input
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-amber-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-amber-200 hover:bg-amber-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * HTTP 401 Unauthorized — Named Component for API Key Failures
 */
export const AuthenticationError: React.FC<ErrorComponentProps> = ({
  rawError,
  onRetry,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-red-500/40 bg-red-950/20 p-5 text-red-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-500/20 text-red-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-red-300">
              Authentication Error (HTTP 401)
            </h4>
            <span className="rounded bg-red-900/60 px-2 py-0.5 text-xs font-mono text-red-300">
              AUTH_FAILURE
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-red-100">
            Access denied: The enterprise API key is missing, invalid, or expired.
          </p>
          <p className="mt-1 text-xs text-red-300/80">
            Suggested Action: Ensure your client provides a valid <code className="rounded bg-red-900/40 px-1 font-mono">x-api-key</code> header or contact your system administrator.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-red-400/90">
              Server diagnostic: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="rounded-lg bg-red-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-400"
              >
                Retry with Active Key
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-red-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-red-200 hover:bg-red-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * HTTP 404 Not Found — Named Component for Session Expiration / Missing UUID
 */
export const SessionNotFoundError: React.FC<ErrorComponentProps> = ({
  rawError,
  onNewSession,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-blue-500/40 bg-blue-950/20 p-5 text-blue-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/20 text-blue-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-blue-300">
              Session Not Found (HTTP 404)
            </h4>
            <span className="rounded bg-blue-900/60 px-2 py-0.5 text-xs font-mono text-blue-300">
              SESSION_NOT_FOUND
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-blue-100">
            The active conversational session has expired from server memory or could not be found.
          </p>
          <p className="mt-1 text-xs text-blue-300/80">
            Suggested Action: Click below to re-initialize an isolated session via <code className="rounded bg-blue-900/40 px-1 font-mono">POST /sessions</code>.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-blue-400/90">
              Server diagnostic: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onNewSession && (
              <button
                type="button"
                onClick={onNewSession}
                className="rounded-lg bg-blue-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                Initialize New Session
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-blue-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-blue-200 hover:bg-blue-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * HTTP 422 Unprocessable Entity — Named Component for Schema / Type Validation Errors
 */
export const ValidationError: React.FC<ErrorComponentProps> = ({
  rawError,
  onRetry,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-purple-500/40 bg-purple-950/20 p-5 text-purple-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-purple-500/20 text-purple-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-purple-300">
              Payload Validation Error (HTTP 422)
            </h4>
            <span className="rounded bg-purple-900/60 px-2 py-0.5 text-xs font-mono text-purple-300">
              UNPROCESSABLE_ENTITY
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-purple-100">
            The request payload failed Pydantic contract validation. Required fields are missing or incorrectly formatted.
          </p>
          <p className="mt-1 text-xs text-purple-300/80">
            Suggested Action: Verify that the query payload includes a non-null string for <code className="rounded bg-purple-900/40 px-1 font-mono">user_input</code> and a valid <code className="rounded bg-purple-900/40 px-1 font-mono">session_id</code>.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-purple-400/90">
              Validation details: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="rounded-lg bg-purple-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-400"
              >
                Re-validate & Retry
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-purple-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-purple-200 hover:bg-purple-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * HTTP 429 Too Many Requests — Named Component for Sliding-Window Rate Limiting
 */
export const RateLimitError: React.FC<ErrorComponentProps> = ({
  rawError,
  onNewSession,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-orange-500/40 bg-orange-950/20 p-5 text-orange-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-orange-500/20 text-orange-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-orange-300">
              Rate Limit Exceeded (HTTP 429)
            </h4>
            <span className="rounded bg-orange-900/60 px-2 py-0.5 text-xs font-mono text-orange-300">
              RATE_LIMIT_EXCEEDED
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-orange-100">
            You&apos;ve reached the request limit (20 requests per hour) for this session.
          </p>
          <p className="mt-1 text-xs text-orange-300/80">
            Suggested Action: Please wait for your 1-hour sliding quota window to recover, or start a new authenticated session.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-orange-400/90">
              Policy detail: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onNewSession && (
              <button
                type="button"
                onClick={onNewSession}
                className="rounded-lg bg-orange-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-400"
              >
                Create Fresh Session
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-orange-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-orange-200 hover:bg-orange-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * HTTP 500 Internal Server Error — Named Component for Pipeline Exceptions
 */
export const InternalServerError: React.FC<ErrorComponentProps> = ({
  rawError,
  onRetry,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-rose-500/40 bg-rose-950/20 p-5 text-rose-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-rose-500/20 text-rose-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-rose-300">
              Internal Server Error (HTTP 500)
            </h4>
            <span className="rounded bg-rose-900/60 px-2 py-0.5 text-xs font-mono text-rose-300">
              INTERNAL_ERROR
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-rose-100">
            The AI reasoning pipeline or SQLite database encountered an unhandled server exception.
          </p>
          <p className="mt-1 text-xs text-rose-300/80">
            Suggested Action: Click retry to re-dispatch the inference request. If persistent, alert the AURONIX SRE team.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-rose-400/90">
              Diagnostics: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="rounded-lg bg-rose-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-rose-500 focus:outline-none focus:ring-2 focus:ring-rose-400"
              >
                Retry Query
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-rose-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-rose-200 hover:bg-rose-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * HTTP 503 Service Unavailable — Named Component for Connection & Upstream Timeouts
 */
export const ServiceUnavailableError: React.FC<ErrorComponentProps> = ({
  rawError,
  onRetry,
  onDismiss,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      className="rounded-xl border border-red-500/40 bg-red-950/20 p-5 text-red-200 shadow-lg backdrop-blur-sm transition-all"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-500/20 text-red-400">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.828m2.829 2.828L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.828m-4.243 4.243a9 9 0 01-12.728 0m0 0l2.828-2.829m-2.828 2.829L3 21m2.828-15.364a9 9 0 0112.728 0" />
          </svg>
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold uppercase tracking-wider text-red-300">
              Service Unavailable (HTTP 503)
            </h4>
            <span className="rounded bg-red-900/60 px-2 py-0.5 text-xs font-mono text-red-300">
              SERVICE_UNAVAILABLE
            </span>
          </div>
          <p className="mt-1 text-sm font-medium text-red-100">
            Cannot establish socket connection with the AURONIX inference cluster.
          </p>
          <p className="mt-1 text-xs text-red-300/80">
            Suggested Action: Check network connectivity or upstream AI provider status and retry.
          </p>
          {rawError && (
            <div className="mt-2 rounded bg-black/40 p-2 font-mono text-[11px] text-red-400/90">
              Network diagnostic: {rawError}
            </div>
          )}
          <div className="mt-3 flex gap-2">
            {onRetry && (
              <button
                type="button"
                onClick={onRetry}
                className="rounded-lg bg-red-600/80 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-500 focus:outline-none focus:ring-2 focus:ring-red-400"
              >
                Reconnect & Retry
              </button>
            )}
            {onDismiss && (
              <button
                type="button"
                onClick={onDismiss}
                className="rounded-lg border border-red-700/50 bg-transparent px-3 py-1.5 text-xs font-medium text-red-200 hover:bg-red-900/30"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Dispatcher Component: Maps any Day-45 HTTP status or error code to its dedicated named component
 */
export const AuronixErrorDispatcher: React.FC<{
  error: ApiErrorDetail;
  onRetry?: () => void;
  onNewSession?: () => void;
  onClearInput?: () => void;
  onDismiss?: () => void;
}> = ({ error, onRetry, onNewSession, onClearInput, onDismiss }) => {
  const code = error.statusCode;

  switch (code) {
    case 400:
      return (
        <InvalidInputError
          rawError={error.rawError || error.message}
          onClearInput={onClearInput}
          onDismiss={onDismiss}
        />
      );
    case 401:
      return (
        <AuthenticationError
          rawError={error.rawError || error.message}
          onRetry={onRetry}
          onDismiss={onDismiss}
        />
      );
    case 404:
      return (
        <SessionNotFoundError
          rawError={error.rawError || error.message}
          onNewSession={onNewSession}
          onDismiss={onDismiss}
        />
      );
    case 422:
      return (
        <ValidationError
          rawError={error.rawError || error.message}
          onRetry={onRetry}
          onDismiss={onDismiss}
        />
      );
    case 429:
      return (
        <RateLimitError
          rawError={error.rawError || error.message}
          onNewSession={onNewSession}
          onDismiss={onDismiss}
        />
      );
    case 503:
      return (
        <ServiceUnavailableError
          rawError={error.rawError || error.message}
          onRetry={onRetry}
          onDismiss={onDismiss}
        />
      );
    case 500:
    default:
      return (
        <InternalServerError
          rawError={error.rawError || error.message}
          onRetry={onRetry}
          onDismiss={onDismiss}
        />
      );
  }
};
