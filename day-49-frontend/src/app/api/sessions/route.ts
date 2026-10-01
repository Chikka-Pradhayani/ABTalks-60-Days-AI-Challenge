import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

const DEFAULT_API_KEY = 'auronix-secret-key-45';

export async function POST(req: NextRequest) {
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

  const sessionId = crypto.randomUUID();
  const createdAt = new Date().toISOString();

  return NextResponse.json(
    {
      success: true,
      session_id: sessionId,
      created_at: createdAt,
      message: 'Session successfully initialized.',
    },
    { status: 201 }
  );
}
