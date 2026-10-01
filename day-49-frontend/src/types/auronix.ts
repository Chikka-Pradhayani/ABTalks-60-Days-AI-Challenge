export interface Citation {
  documentName: string;
  excerpt: string;
  similarityScore: number;
}

export interface AskResponseMetadata {
  sessionId: string;
  latencyMs: number;
  retrievalScore: number;
  timestamp: string;
  citations: Citation[];
}

export type StreamState = 'idle' | 'skeleton' | 'streaming' | 'completed' | 'error';

export interface FeedbackRequest {
  session_id: string;
  query_reference?: string;
  feedback_type: 'grounding_accuracy' | 'relevance' | 'hallucination_report' | 'general';
  rating: 'positive' | 'negative';
  comment?: string;
}

export interface FeedbackResponse {
  success: boolean;
  feedback_id: number;
  message: string;
  timestamp: string;
}

export interface ApiErrorDetail {
  statusCode: number;
  errorCode: string;
  message: string;
  rawError?: string;
  suggestedAction: string;
}
