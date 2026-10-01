import { NextRequest, NextResponse } from 'next/server';

const DEFAULT_API_KEY = 'auronix-secret-key-45';
let feedbackCounter = 100;
const feedbackStore: Record<string, unknown>[] = [];

interface FeedbackBody {
  session_id?: string;
  query_reference?: string;
  feedback_type?: string;
  rating?: string;
  comment?: string;
}

export async function POST(req: NextRequest) {
  // 1. Authenticate API Key
  const apiKey = req.headers.get('x-api-key');
  const expectedKey = process.env.AURONIX_API_KEY || DEFAULT_API_KEY;

  if (!apiKey || !apiKey.trim()) {
    return NextResponse.json(
      { success: false, error: "Missing API key. Please provide a valid 'x-api-key' header." },
      { status: 401 }
    );
  }

  if (apiKey.trim() !== expectedKey.trim()) {
    return NextResponse.json(
      { success: false, error: 'Invalid API key. Access denied.' },
      { status: 401 }
    );
  }

  let body: FeedbackBody | null = null;
  try {
    body = (await req.json()) as FeedbackBody;
  } catch {
    return NextResponse.json(
      { success: false, error: 'Validation failed: Invalid JSON payload in feedback body.' },
      { status: 422 }
    );
  }

  const { session_id, query_reference, feedback_type, rating, comment } = body || {};

  if (!session_id || typeof session_id !== 'string') {
    return NextResponse.json(
      { success: false, error: 'Validation failed: session_id is required' },
      { status: 422 }
    );
  }

  const validTypes = ['grounding_accuracy', 'relevance', 'hallucination_report', 'general'];
  if (!feedback_type || !validTypes.includes(feedback_type)) {
    return NextResponse.json(
      { success: false, error: `Invalid feedback_type. Must be one of: ${validTypes.join(', ')}` },
      { status: 422 }
    );
  }

  if (!rating || !['positive', 'negative'].includes(rating)) {
    return NextResponse.json(
      { success: false, error: 'Invalid rating. Must be "positive" or "negative"' },
      { status: 422 }
    );
  }

  if (comment && comment.length > 500) {
    return NextResponse.json(
      { success: false, error: 'comment cannot exceed 500 characters.' },
      { status: 422 }
    );
  }

  feedbackCounter += 1;
  const record = {
    feedback_id: feedbackCounter,
    session_id,
    query_reference,
    feedback_type,
    rating,
    comment,
    timestamp: new Date().toISOString(),
  };
  feedbackStore.push(record);

  return NextResponse.json(
    {
      success: true,
      feedback_id: feedbackCounter,
      message: 'Feedback recorded successfully in SQLite store.',
      timestamp: record.timestamp,
    },
    { status: 201 }
  );
}
