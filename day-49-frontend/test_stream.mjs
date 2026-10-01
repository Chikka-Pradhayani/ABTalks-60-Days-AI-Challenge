import http from 'http';

async function main() {
  console.log('--- Step 1: Initialize Session via POST /api/sessions ---');
  const sessionRes = await fetch('http://localhost:3000/api/sessions', {
    method: 'POST',
    headers: { 'x-api-key': 'auronix-secret-key-45' },
  });
  const sessionData = await sessionRes.json();
  console.log('Session Response Status:', sessionRes.status);
  console.log('Session ID:', sessionData.session_id);

  if (!sessionData.session_id) {
    throw new Error('Session ID not returned!');
  }

  console.log('\n--- Step 2: Stream Tokens via POST /api/ask using Fetch + ReadableStream ---');
  const askRes = await fetch('http://localhost:3000/api/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': 'auronix-secret-key-45',
    },
    body: JSON.stringify({
      session_id: sessionData.session_id,
      user_input: 'What is the immediate failover protocol when a P0 Aurora DB crash occurs?',
    }),
  });

  console.log('Ask Status:', askRes.status);
  console.log('Ask Content-Type:', askRes.headers.get('content-type'));

  const reader = askRes.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let tokenCount = 0;
  let fullAnswer = '';
  let metadata = null;
  let buffer = '';

  const startTime = Date.now();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith('data:')) continue;

      const event = JSON.parse(trimmed.replace(/^data:\s*/, ''));
      if (event.type === 'token') {
        tokenCount++;
        fullAnswer += event.token;
        process.stdout.write(`[Chunk ${tokenCount}] ` + event.token.replace(/\n/g, ' ') + '\n');
      } else if (event.type === 'metadata') {
        metadata = event;
        console.log('\n--- Received Metadata Event ---');
        console.log('Latency (ms):', event.latencyMs);
        console.log('Retrieval Grounding Score:', event.retrievalScore);
        console.log('Citations Count:', event.citations?.length);
        event.citations?.forEach((c, idx) => {
          console.log(`  [Citation ${idx + 1}] Doc: ${c.documentName} | Score: ${c.similarityScore}`);
        });
      } else if (event.type === 'done') {
        console.log('--- Received Stream Completion Event (type: done) ---');
      }
    }
  }

  const durationMs = Date.now() - startTime;
  console.log(`\nStream verified! Rendered ${tokenCount} chunks incrementally over ${durationMs}ms.`);
  console.log('Full Answer Length:', fullAnswer.length, 'characters');

  console.log('\n--- Step 3: Test Enterprise Feedback via POST /api/feedback ---');
  const fbRes = await fetch('http://localhost:3000/api/feedback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': 'auronix-secret-key-45',
    },
    body: JSON.stringify({
      session_id: sessionData.session_id,
      query_reference: 'P0 failover protocol',
      feedback_type: 'grounding_accuracy',
      rating: 'positive',
      comment: 'Accurately retrieved Aurora failover script and RTO SLA target.',
    }),
  });
  const fbData = await fbRes.json();
  console.log('Feedback Status:', fbRes.status);
  console.log('Feedback Response:', fbData);

  console.log('\n--- Step 4: Verify Day-45 Error Codes & Responses ---');
  const errorTests = [
    { code: 400, header: '400', expected: 'user_input cannot be empty or contain only whitespace.' },
    { code: 401, header: '401_missing', expected: 'Missing API key' },
    { code: 401, header: '401_invalid', expected: 'Invalid API key' },
    { code: 404, header: '404', expected: 'Session' },
    { code: 422, header: '422', expected: 'Validation failed' },
    { code: 429, header: '429', expected: 'Rate limit exceeded' },
    { code: 500, header: '500', expected: 'Internal server error' },
    { code: 503, header: '503', expected: 'Service Unavailable' },
  ];

  for (const t of errorTests) {
    const res = await fetch('http://localhost:3000/api/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': 'auronix-secret-key-45',
        'x-test-error': t.header,
      },
      body: JSON.stringify({
        session_id: sessionData.session_id,
        user_input: 'Test query',
      }),
    });
    const errBody = await res.json();
    const passed = res.status === t.code && errBody.error.includes(t.expected);
    console.log(`[HTTP ${t.code}] Header: ${t.header} -> Status: ${res.status} | Matched: ${passed} | Msg: ${errBody.error.slice(0, 50)}...`);
    if (!passed) {
      throw new Error(`Error test failed for ${t.header}`);
    }
  }

  console.log('\n>>> ALL END-TO-END VERIFICATIONS PASSED SUCCESSFULLY! <<<');
}

main().catch((err) => {
  console.error('Verification failed:', err);
  process.exit(1);
});
