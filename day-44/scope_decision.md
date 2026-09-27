# AURONIX Scope Decision Document — Day 44

## Executive Summary
This document establishes the architectural boundaries for the **AURONIX Minimum Viable Product (MVP)**. Following MVP engineering principles, the objective of Day 44 is to define the minimum feature set required to validate the core value hypothesis—*converting an employee query into a grounded, useful answer via an AI model*—while strictly deferring non-essential secondary capabilities.

---

## 1. MVP Capabilities (Included in Scope)
These capabilities represent the minimum operational core required to prove technical feasibility and user value:

1. **Single-Turn Natural Language Query Ingestion:** Direct text ingestion of employee questions via JSON payload.
2. **Input Validation & Sanitization:** Enforcing non-empty strings and whitespace stripping using Pydantic schemas.
3. **Core AI Interaction Loop (`core_ai_loop`):** A standalone, decoupled function that packages prompts, manages system context, and calls OpenAI chat completions.
4. **Environment-Based Credential Isolation:** Zero-secret code architecture reading `OPENAI_API_KEY` and `OPENAI_MODEL` from environment variables.
5. **REST API Gateway (`POST /ask`):** A lightweight FastAPI endpoint providing a standardized interface for client integrations.
6. **Structured JSON Response & Error Contracts:** Predictable responses (`{success: true, answer: ...}` vs `{success: false, error: ...}`) across HTTP status codes.

---

## 2. Post-MVP Capabilities (Excluded from Scope)

Every excluded capability below is deferred beyond the Day 44 MVP to keep the core loop simple, isolated, and verifiable.

| # | Deferred Capability | Category | Exact Exclusion Rationale |
|---|---|---|---|
| **1** | **Multi-Turn Conversation History** | Interaction Layer | Deferring session memory avoids stateful database management overhead while validating single-turn query comprehension. |
| **2** | **Role-Based Access Control (RBAC) Gating** | Security & Auth | Deferring authorization boundaries isolates model response generation from complex enterprise permission graphs. |
| **3** | **Real-Time Streaming Responses (SSE / WebSockets)** | Transport Layer | Deferring streaming minimizes HTTP connection complexity until the core REST request-response cycle is verified. |
| **4** | **Enterprise Single Sign-On (SAML / OIDC)** | Identity Management | Deferring federated authentication eliminates third-party IdP dependency during initial core loop testing. |
| **5** | **Multi-Format Live Ingestion Connectors (Confluence / Jira)** | Data Pipeline | Deferring automated SaaS connectors keeps Day 44 focused on inference rather than data scraping. |
| **6** | **Voice Interface (Browser Speech STT/TTS Telemetry)** | Modality | Deferring speech synthesis and audio capture avoids browser Web Speech API inconsistencies during backend evaluation. |
| **7** | **Interactive Web Frontend / Chat Dashboard** | User Interface | Deferring frontend UI allows 100% of engineering bandwidth to focus on API stability and model grounding. |
| **8** | **Document Versioning & Temporal Diff Tracking** | Knowledge Base | Deferring historical document diffing avoids complex temporal vector index invalidation in the initial prototype. |
| **9** | **User Feedback Loop & RLHF Rating Buttons (Thumbs Up/Down)** | Model Optimization | Deferring feedback collection saves database write schemas until active employee query traffic exists. |
| **10**| **Administrative Analytics & Usage Telemetry Dashboard** | Observability | Deferring aggregate analytics dashboards prevents premature optimization before core product adoption. |
| **11**| **Multi-Language Translation & Localization** | Natural Language Processing | Deferring multi-language tokenization eliminates prompt bloat for English-first corporate documentation. |
| **12**| **Automated Query Intent Classification & Routing** | Orchestration | Deferring multi-agent intent routers maintains a single, highly debuggable linear execution pipeline. |

---

## 3. Decision Matrix Summary
* **Total Capabilities Evaluated:** 18
* **Capabilities in MVP Scope:** 6
* **Capabilities in Post-MVP Scope:** 12
* **Architectural Guiding Principle:** Build the smallest possible loop that proves the product's primary interaction before introducing distributed state, UI, or enterprise infrastructure.
