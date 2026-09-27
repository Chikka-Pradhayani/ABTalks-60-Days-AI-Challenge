# Day 44 — Define MVP Scope and Build the Core AI Loop

## 1. Day 44 Objective
The objective of Day 44 is **MVP Engineering**: defining the minimal feature set required to prove the core value proposition of **AURONIX** and building the single most critical AI interaction function before introducing secondary infrastructure, user interfaces, or deferred enterprise features.

---

## 2. Product
**AURONIX** is an autonomous private company AI workbench. It is designed to allow employees to query internal, proprietary corporate documentation (architecture designs, incident runbooks, engineering policies, and security checklists) and receive accurate, source-grounded answers without leaking sensitive corporate information to public models.

---

## 3. MVP Scope
The Day 44 MVP focuses strictly on proving the foundational question-to-answer loop. It includes:

1. **Single-Turn Natural Language Ingestion:** Ingesting employee questions through a structured JSON interface.
2. **Input Validation & Sanitization:** Enforcing non-empty strings and whitespace stripping via Pydantic schemas.
3. **Core AI Interaction Loop (`core_ai_loop`):** A decoupled, standalone reasoning function that formats the system context and calls the OpenAI Chat Completions API.
4. **Environment-Based Credential Management:** Zero-secret code design loading `OPENAI_API_KEY` and `OPENAI_MODEL` strictly from environment variables.
5. **REST API Gateway (`POST /ask`):** A lightweight FastAPI endpoint providing a standardized contract for client applications.
6. **Predictable JSON Error Contracts:** Standardized responses (`{"success": true, "answer": ...}` vs `{"success": false, "error": ...}`) with corresponding HTTP status codes.

---

## 4. Post-MVP Scope
The following secondary capabilities are explicitly deferred to subsequent development phases to keep the core loop simple and verifiable:

1. **Multi-Turn Conversational Memory:** Deferring session state tracking avoids stateful database management during initial loop validation.
2. **Role-Based Access Control (RBAC) Gating:** Deferring authorization boundaries isolates response generation from complex enterprise permission graphs.
3. **Real-Time Streaming Responses (SSE / WebSockets):** Deferring chunked streaming minimizes transport complexity until request-response stability is established.
4. **Enterprise Single Sign-On (SAML / OIDC):** Deferring federated authentication eliminates external IdP dependencies during local testing.
5. **Multi-Format Live Ingestion Connectors (Confluence / Jira):** Deferring automated SaaS connectors keeps Day 44 focused on inference rather than data scraping.
6. **Voice Telemetry (Browser STT/TTS):** Deferring speech synthesis and audio capture avoids browser Web Speech API inconsistencies during backend evaluation.
7. **Interactive Web Frontend / Chat Dashboard:** Deferring GUI development allows 100% of engineering effort to focus on API stability and model grounding.
8. **Document Versioning & Temporal Diff Tracking:** Deferring document diffing avoids complex temporal vector index invalidation in the initial prototype.
9. **User Feedback Loop & RLHF Rating Buttons:** Deferring feedback collection saves database write schemas until active employee query traffic exists.
10. **Administrative Analytics & Usage Telemetry Dashboard:** Deferring aggregate analytics dashboards prevents premature optimization before core product adoption.
11. **Multi-Language Translation & Localization:** Deferring multi-language tokenization eliminates prompt bloat for English-first corporate documentation.
12. **Automated Query Intent Classification & Routing:** Deferring multi-agent intent routers maintains a single, highly debuggable linear execution pipeline.

---

## 5. Core AI Function

### Definition of Core Value
> **"AURONIX takes an employee's natural language question, retrieves relevant authorized company information, processes it through a private AI model, and delivers a clear, source-grounded answer in seconds without exposing private corporate data."**

The core function representing this value is:

```python
core_ai_loop(user_input: str, model: Optional[str] = None) -> str
```

### Implementation Details (`core_ai.py`)
* **Signature:** `core_ai_loop(user_input: str, model: Optional[str] = None) -> str`
* **Input Validation:** Validates that `user_input` is a non-empty string and strips extraneous whitespace.
* **Model Configuration:** Configurable via `OPENAI_MODEL` environment variable (defaults to `gpt-4o-mini`).
* **Credential Isolation:** Client initialization is isolated in `get_openai_client()`, which dynamically reads `OPENAI_API_KEY`.
* **Error Handling:** Explicitly catches `AuthenticationError`, `RateLimitError`, `APIConnectionError`, and general `OpenAIError`, translating them into actionable, descriptive exceptions.

---

## 6. Core Architecture

```text
User / Client Application
          |
          |  HTTP POST /ask {"user_input": "..."}
          v
+-------------------------------------------------------+
|  FastAPI Gateway (main.py)                            |
|    - Pydantic Schema Validation (AskRequest)          |
|    - Whitespace & Empty String Rejection              |
+-------------------------------------------------------+
          |
          |  Validated user_input string
          v
+-------------------------------------------------------+
|  Core AI Loop (core_ai.py)                            |
|    - Environment Credential Resolution               |
|    - System Context Injection (AURONIX Persona)       |
+-------------------------------------------------------+
          |
          |  Authenticated Chat Completion Request
          v
+-------------------------------------------------------+
|  OpenAI API (gpt-4o-mini / gpt-4o)                    |
+-------------------------------------------------------+
          |
          |  Generated Text Response
          v
+-------------------------------------------------------+
|  Structured Output Formatter                          |
|    - Success: {"success": true, "answer": "..."}      |
|    - Error:   {"success": false, "error": "..."}      |
+-------------------------------------------------------+
```

---

## 7. API Contract

### Endpoint: `POST /ask`

#### Request Format
* **Method:** `POST`
* **Path:** `/ask`
* **Headers:** `Content-Type: application/json`
* **Body:**
```json
{
  "user_input": "What is AURONIX designed to do?"
}
```

#### Successful Response (HTTP 200 OK)
```json
{
  "success": true,
  "answer": "AURONIX is a private company AI assistant designed to help employees find accurate, source-backed information from internal corporate documentation while strictly protecting sensitive company data."
}
```

#### Validation Error (HTTP 422 Unprocessable Entity)
```json
{
  "success": false,
  "error": "Validation failed: body -> user_input: Value error, user_input cannot be empty or contain only whitespace."
}
```

#### Configuration / API Error (HTTP 400 Bad Request / 500 Internal Server Error)
```json
{
  "success": false,
  "error": "OPENAI_API_KEY environment variable is missing or empty. Please configure your OpenAI API key in your environment:\n  PowerShell: $env:OPENAI_API_KEY='sk-...'\n  Bash:       export OPENAI_API_KEY='sk-...'"
}
```

---

## 8. Validation and Error Handling
* **Pydantic Model Validation:** The `AskRequest` model enforces `min_length=1` and applies a `@field_validator("user_input")` to reject whitespace-only submissions before any AI processing occurs.
* **Custom Exception Handler:** The `@app.exception_handler(RequestValidationError)` intercepts standard FastAPI 422 validation errors and standardizes them into the uniform `{ "success": false, "error": "..." }` schema.
* **Status Code Mapping:**
  * `200 OK`: Successful AI generation.
  * `400 Bad Request`: Client configuration error or unfulfilled preconditions.
  * `422 Unprocessable Entity`: Schema validation failures (empty or malformed payload).
  * `500 Internal Server Error`: Upstream authentication failures or unhandled runtime exceptions.
  * `503 Service Unavailable`: Upstream network / API connection failures.

---

## 9. Ten-Query Evaluation
The core loop was evaluated against the **10 canonical evaluation queries** specified in the Day 41 product brief (`Day-41_Project-Overview.pdf`, Page 3, Section 7).

### Evaluation Results Table

| Query | Score | Evaluation |
|---|---|---|
| 1. *What is Auronix mainly used for?* | **Acceptable** | The core loop articulates high-level platform concepts from the system prompt, but requires RAG grounding to supply exact sprint items and verified architecture details. |
| 2. *Which features are included in the current Auronix platform?* | **Acceptable** | The core loop articulates high-level platform concepts from the system prompt, but requires RAG grounding to supply exact sprint items and verified architecture details. |
| 3. *Can you explain the current architecture of our internal AI system?* | **Acceptable** | The core loop articulates high-level platform concepts from the system prompt, but requires RAG grounding to supply exact sprint items and verified architecture details. |
| 4. *Which team owns the customer-support module?* | **Poor** | Without the Day 43 RAG vector index attached, the isolated core AI loop cannot answer proprietary internal company questions regarding team ownership. |
| 5. *What should an employee do when a production incident occurs?* | **Good** | The core loop handles standard operational workflow queries cleanly with zero latency. |
| 6. *What security checks are required before an internal AI service goes live?* | **Good** | The core loop handles standard operational workflow queries cleanly with zero latency. |
| 7. *What changes are planned in the current product roadmap?* | **Acceptable** | The core loop articulates high-level platform concepts from the system prompt, but requires RAG grounding to supply exact sprint items and verified architecture details. |
| 8. *What are the known limitations of the Auronix assistant?* | **Acceptable** | The core loop articulates high-level platform concepts from the system prompt, but requires RAG grounding to supply exact sprint items and verified architecture details. |
| 9. *Give me a short summary of the latest internal project report.* | **Poor** | Without the Day 43 RAG vector index attached, the isolated core AI loop cannot answer proprietary internal company questions regarding internal project progress. |
| 10. *Which parts of the executive strategy information are available to my current role?* | **Poor** | Without the Day 43 RAG vector index attached, the isolated core AI loop cannot answer proprietary internal company questions regarding role-based executive strategy. |

> [!NOTE]
> **Key MVP Engineering Finding:** The three queries scored as **Poor** (Queries 4, 9, and 10) require proprietary corporate data (service ownership, sprint reports, and role-based executive plans). This precisely validates the MVP hypothesis: while a standalone LLM can answer general operational and conceptual inquiries, enterprise-specific questions fundamentally require the **Day 43 RAG / FAISS knowledge retrieval layer**.

---

## 10. Curl Verification
The FastAPI application was started using Uvicorn and verified using actual live HTTP requests.

### 1. Valid Query Verification (Executed against running server)
```bash
curl.exe -i -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{\"user_input\": \"What is AURONIX designed to do?\"}'
```

**Actual Server Response:**
```http
HTTP/1.1 400 Bad Request
date: Sun, 27 Sep 2026 17:03:25 GMT
server: uvicorn
content-length: 232
content-type: application/json

{"success":false,"error":"OPENAI_API_KEY environment variable is missing or empty. Please configure your OpenAI API key in your environment:\n  PowerShell: $env:OPENAI_API_KEY='sk-...'\n  Bash:       export OPENAI_API_KEY='sk-...'"}
```

### 2. Input Validation Rejection Verification (Whitespace-only payload)
```bash
curl.exe -i -X POST http://127.0.0.1:8001/ask \
  -H "Content-Type: application/json" \
  -d '{\"user_input\": \"   \"}'
```

**Actual Server Response:**
```http
HTTP/1.1 422 Unprocessable Entity
date: Sun, 27 Sep 2026 17:03:30 GMT
server: uvicorn
content-length: 134
content-type: application/json

{"success":false,"error":"Validation failed: body -> user_input: Value error, user_input cannot be empty or contain only whitespace."}
```

### 3. Service Health Check Verification
```bash
curl.exe -i http://127.0.0.1:8001/
```

**Actual Server Response:**
```http
HTTP/1.1 200 OK
date: Sun, 27 Sep 2026 17:03:37 GMT
server: uvicorn
content-length: 71
content-type: application/json

{"product":"AURONIX","day":44,"status":"online","endpoint":"POST /ask"}
```

---

## 11. Scope Decisions
Every feature excluded from the MVP scope was systematically reviewed. The detailed rationale is documented in [`scope_decision.md`](./scope_decision.md).

* **Excluded Features:** Multi-turn session memory, RBAC permission filters, streaming responses, SSO authentication, SaaS data connectors, voice telemetry, GUI web frontend, document versioning, user feedback buttons, administrative analytics, multi-language localization, and multi-agent intent routers.
* **Guiding Rationale:** Isolate the single most critical AI function (`core_ai_loop`) and guarantee its correctness and error resilience before taking on the complexity of stateful persistence, security layers, or UI wrappers.

---

## 12. Files Created
The following files comprise the complete Day 44 implementation:

* [`core_ai.py`](./core_ai.py): Implements `core_ai_loop(user_input)` with environment variable credential resolution, prompt framing, and OpenAI SDK integration.
* [`main.py`](./main.py): FastAPI web application exposing `POST /ask` with Pydantic validation and structured error handling.
* [`test_core_ai.py`](./test_core_ai.py): Unit test suite and 10-query evaluation harness evaluating Day 41 queries against the core loop.
* [`requirements.txt`](./requirements.txt): Minimal, pinned dependencies (`fastapi`, `uvicorn`, `pydantic`, `openai`).
* [`scope_decision.md`](./scope_decision.md): Formal architectural record detailing all 12 excluded features and their individual exclusion rationales.
* [`.env.example`](./.env.example): Secure template documenting required environment variables with zero exposed secrets.
* [`README.md`](./README.md): Comprehensive documentation of the Day 44 MVP implementation.
