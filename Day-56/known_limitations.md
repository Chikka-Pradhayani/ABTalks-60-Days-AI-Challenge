# Day 56 — Known Limitations & Architectural Hardening Roadmap

**System:** AURONIX Autonomous Private Enterprise AI Workbench  
**Document Status:** Official Production Release Limitations Assessment  
**Audit Date:** 2026-10-08  

---

## 1. Executive Summary

Transparent system characterization is essential for production deployment. This document catalogs the known boundaries, performance thresholds, failure modes, and architectural trade-offs of the AURONIX system. 

Where metrics have been empirically benchmarked in previous evaluation phases (such as Day 50 and Day 52), verified figures are cited. Where specific stress boundaries or saturation points have not been empirically tested, they are explicitly designated as **Not measured** in accordance with engineering integrity principles.

---

## 2. Current Limitations

1. **Static Knowledge Base Scope:**  
   AURONIX operates on a curated 50-chunk enterprise knowledge base (`day-50/knowledge_base.py`). It cannot dynamically ingest external websites, real-time Slack threads, or live Jira tickets at runtime without a knowledge re-indexing cycle.
2. **Tabular & Quantitative Computation:**  
   While AURONIX excels at qualitative runbook retrieval and architectural specification matching, complex arithmetic or financial calculations across tabular spreadsheets are not natively supported by the keyword/semantic retrieval layer.
3. **Multi-turn Conversational Memory:**  
   The system implements session isolation via `session_id`, but each query to `POST /ask` is currently treated as an independent retrieval execution rather than maintaining multi-turn conversational coreference resolution.

---

## 3. Performance Limitations

- **Warm In-Memory Latency:** **$\approx 15\text{ms} - 25\text{ms}$** per grounded query on local hardware with in-memory semantic caching enabled.
- **Cold Boot Latency:** **$\approx 700\text{ms} - 800\text{ms}$** on initial container startup when initializing the FAISS vector index and embedding representations.
- **Concurrent Request Throughput:** **Not measured**. High-concurrency saturation testing (e.g., 500+ simultaneous concurrent requests via Locust/k6) has not been empirically conducted on the single-worker Uvicorn process.
- **Cache Memory Capacity Saturation:** **Not measured**. In-memory semantic cache currently holds up to 1,000 entries with LRU eviction; memory consumption under $\ge 100,000$ unique cache keys has not been measured under production constraints.
- **Query Complexity Degradation:** Latency remains stable ($<50\text{ms}$) up to 4,000 characters. For queries exceeding 4,000 characters, requests are deterministically rejected with HTTP 422 to prevent buffer exhaustion.

---

## 4. Quality Limitations

- **Complex Multi-Hop Cross-Domain Synthesis (4+ Documents):**  
   Queries requiring the simultaneous synthesis of more than three disparate corporate documents (e.g., correlating HR compensation matrices, AWS IAM infrastructure, and legal terms in a single prompt) occasionally suffer from facet omission.
- **Adversarial Obfuscation:**  
   While standard false premises (e.g., *"AURONIX reboots cloud datacenters on 15s lag"*) are effectively refuted, highly sophisticated adversarial jailbreaks utilizing multi-lingual or cipher-encoded prompts have not been exhaustively evaluated.
- **Synonym Discrepancies:**  
   Queries using non-standard corporate jargon or obscure acronyms not present in the semantic index may fail to trigger vector proximity, resulting in fallback responses.

---

## 5. Reliability Limitations

- **SQLite Write Lock Contention:**  
   AURONIX utilizes SQLite (`auronix_production.db`) for session logging, request auditing, and feedback storage. Under heavy burst write traffic across multiple parallel threads, SQLite can encounter `sqlite3.OperationalError: database is locked`. (Mitigated in Day 56 with structured logging warnings, but still an engine limitation compared to PostgreSQL).
- **Container Ephemeral Disk Reset:**  
   In cloud environments without a persistent volume mount attached to `/app/data`, SQLite databases and FAISS indexes will reset to initial state whenever the container restarts or re-deploys.
- **Single Process Uvicorn Worker:**  
   The default server runs a single Uvicorn process. A CPU-bound task in the main thread can briefly block the event loop for subsequent requests.

---

## 6. Security Limitations

- **In-Memory Rate Limiting Volatility:**  
   The sliding-window rate limiter stores timestamp history in process memory (`session_request_timestamps: Dict[str, List[float]]`). If the server restarts or scales horizontally across multiple container instances, rate limit counters reset to zero.
- **Shared API Key Model:**  
   All clients in an environment authenticate against a single shared environment variable key (`AURONIX_API_KEY`). Fine-grained, per-user RBAC tokens with automated revocation are not yet implemented.
- **Absence of Hardware Security Module (HSM):**  
   Secrets are managed via environment variables rather than a dedicated cloud KMS / HashiCorp Vault integration.

---

## 7. Infrastructure Limitations

- **Cloud Platform Dependency:**  
   Railway deployment requires pre-provisioned project tokens and valid build credit balance. If secrets are missing in GitHub Actions, container staging/production promotion steps are skipped.
- **Vector Index Synchronization:**  
   FAISS vector indexes are generated as binary artifacts (`faiss_index_production.bin`). There is no automated distributed vector sync (e.g., Milvus, Pinecone, Qdrant) across multi-region deployments.

---

## 8. Priority Improvements Roadmap (Next Two Weeks)

If granted two additional development weeks prior to general commercial launch, improvements are ranked by priority:

### Tier 1: Critical Priority
1. **Migrate SQLite Persistence to Managed PostgreSQL:**  
   Replace SQLite with Amazon RDS or Railway PostgreSQL to eliminate file-level write lock contention and guarantee transactional ACID durability across multi-instance clusters.
2. **Distributed Redis-Backed Rate Limiter:**  
   Replace in-memory rate limiting dictionary with Redis atomic sliding-window counter (`ZADD` / `ZREMRANGEBYSCORE`) ensuring global throttling across scaled workers.

### Tier 2: High Priority
3. **Automated Multi-Turn Dialogue Memory:**  
   Implement a conversational buffer memory with session TTL, enabling follow-up questions without repeating context.
4. **Per-User Role-Based Access Control (RBAC):**  
   Implement JWT or OAuth2 bearer authentication with role scopes (`admin`, `engineer`, `compliance`) replacing the single static `x-api-key`.

### Tier 3: Medium Priority
5. **Continuous Dynamic Knowledge Ingestion:**  
   Build an asynchronous document indexing worker that polls Notion/GitHub Markdown documentation and rebuilds FAISS embeddings incrementally.
6. **High-Concurrency Load Testing:**  
   Execute full load and stress testing using Locust to measure latency, throughput (RPS), and p99 degradation under 1,000 concurrent sessions.

### Tier 4: Low Priority
7. **Semantic Cache Memory Tiering:**  
   Implement persistent disk-spill for semantic cache keys to prevent memory exhaustion under 500,000+ cached interactions.
8. **Multi-Model Dynamic Routing:**  
   Route simple factual lookups to lightweight models while directing multi-hop synthesis to reasoning-heavy models to optimize cost.
