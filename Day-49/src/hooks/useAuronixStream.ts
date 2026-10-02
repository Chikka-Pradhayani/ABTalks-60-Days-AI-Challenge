'use client';

import { useState, useRef, useCallback } from 'react';
import { AskResponseMetadata, StreamState, ApiErrorDetail } from '@/types/auronix';

interface UseAuronixStreamProps {
  apiKey?: string;
}

export function useAuronixStream({ apiKey = 'auronix-secret-key-45' }: UseAuronixStreamProps = {}) {
  const [streamState, setStreamState] = useState<StreamState>('idle');
  const [streamedContent, setStreamedContent] = useState<string>('');
  const [tokenCount, setTokenCount] = useState<number>(0);
  const [metadata, setMetadata] = useState<AskResponseMetadata | null>(null);
  const [apiError, setApiError] = useState<ApiErrorDetail | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setStreamState('idle');
    setStreamedContent('');
    setTokenCount(0);
    setMetadata(null);
    setApiError(null);
  }, []);

  const sendQuery = useCallback(
    async (
      sessionId: string,
      userInput: string,
      options?: {
        testErrorHeader?: string;
        customApiKey?: string;
      }
    ) => {
      // Clean previous state
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      const controller = new AbortController();
      abortControllerRef.current = controller;

      setApiError(null);
      setStreamedContent('');
      setTokenCount(0);
      setMetadata(null);

      // Transition to State 1: Skeleton Loader
      setStreamState('skeleton');

      try {
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
          'x-api-key': options?.customApiKey !== undefined ? options.customApiKey : apiKey,
        };

        if (options?.testErrorHeader) {
          headers['x-test-error'] = options.testErrorHeader;
        }

        const response = await fetch('/api/ask', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            session_id: sessionId,
            user_input: userInput,
          }),
          signal: controller.signal,
        });

        // Handle Non-200 Responses using Day-45 error schemas
        if (!response.ok) {
          let errPayload: Record<string, string> = {};
          try {
            errPayload = (await response.json()) as Record<string, string>;
          } catch {
            errPayload = { error: response.statusText };
          }

          const rawError = errPayload.error || 'Unknown error occurred.';
          let errorCode = 'API_ERROR';
          let suggestedAction = 'Please check your inputs and try again.';

          switch (response.status) {
            case 400:
              errorCode = 'INVALID_INPUT';
              suggestedAction = 'Enter a specific operational or technical query.';
              break;
            case 401:
              errorCode = 'AUTH_FAILURE';
              suggestedAction = "Verify your corporate API key ('x-api-key').";
              break;
            case 404:
              errorCode = 'SESSION_NOT_FOUND';
              suggestedAction = 'Initialize a new session via POST /sessions.';
              break;
            case 422:
              errorCode = 'UNPROCESSABLE_ENTITY';
              suggestedAction = 'Verify request payload structure.';
              break;
            case 429:
              errorCode = 'RATE_LIMIT_EXCEEDED';
              suggestedAction = 'Wait for your hourly window to reset or start a new session.';
              break;
            case 503:
              errorCode = 'SERVICE_UNAVAILABLE';
              suggestedAction = 'Check network connectivity or backend host status.';
              break;
            case 500:
            default:
              errorCode = 'INTERNAL_ERROR';
              suggestedAction = 'Retry query or contact AURONIX SRE support.';
              break;
          }

          setApiError({
            statusCode: response.status,
            errorCode,
            message: rawError,
            rawError,
            suggestedAction,
          });
          setStreamState('error');
          return;
        }

        // Section 2: ReadableStream progressive token reader
        if (!response.body) {
          throw new Error('Response body does not expose a readable stream.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let accumulatedText = '';
        let receivedTokens = 0;
        let buffer = '';
        let hasStartedStreaming = false;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith('data:')) continue;

            const jsonStr = trimmed.replace(/^data:\s*/, '');
            try {
              const event = JSON.parse(jsonStr);

              if (event.type === 'token') {
                if (!hasStartedStreaming) {
                  // Transition to State 2: Typing / Streaming Indicator
                  hasStartedStreaming = true;
                  setStreamState('streaming');
                }
                accumulatedText += event.token;
                receivedTokens += 1;
                setStreamedContent(accumulatedText);
                setTokenCount(receivedTokens);
              } else if (event.type === 'metadata') {
                setMetadata({
                  sessionId: event.sessionId,
                  latencyMs: event.latencyMs,
                  retrievalScore: event.retrievalScore,
                  timestamp: event.timestamp,
                  citations: event.citations || [],
                });
              } else if (event.type === 'done') {
                // Detected stream completion
                setStreamState('completed');
              }
            } catch (err) {
              console.warn('Failed to parse SSE event:', jsonStr, err);
            }
          }
        }

        // Stream reader finished. Preserve final complete response (State 3)
        setStreamState('completed');
      } catch (err: unknown) {
        if (err instanceof Error && err.name === 'AbortError') {
          setStreamState('idle');
          return;
        }

        const msg = err instanceof Error ? err.message : 'Network connection failed.';
        setApiError({
          statusCode: 503,
          errorCode: 'CONNECTION_FAILURE',
          message: msg,
          suggestedAction: 'Verify local Next.js dev server status and network connectivity.',
        });
        setStreamState('error');
      }
    },
    [apiKey]
  );

  return {
    streamState,
    streamedContent,
    tokenCount,
    metadata,
    apiError,
    sendQuery,
    reset,
  };
}
