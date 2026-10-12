# 60 Days of AI Engineering: What I Built, What Broke, and What I Learned 🚀

**Author:** Pradhayani Chikka  
**Publication Platform:** LinkedIn Long-Form Article  
**Date:** 2026-10-12  

---

## The Graduation Milestone

Sixty consecutive days ago, I embarked on the **ABTalks 60 Days AI Engineering Challenge**. 

Like many software engineers exploring artificial intelligence, I started with basic exploratory scripts and prompt experiments. But as anyone who has attempted to take generative AI into real-world production knows: **calling an LLM API does not make you an AI engineer**.

Real AI engineering begins when the "magic" wears off. It begins when an upstream model hallucinates an invalid database failover command during a simulated outage, when a loose semantic cache confuses database replication with Redis key eviction, when a two-column PDF scrambles an incident runbook into gibberish, and when users pose adversarial questions that trick foundation models into sycophantic agreement.

Today, on **Day 60**, I am officially graduating from the challenge. Over sixty days, I moved from foundational machine learning intuitions to architecting, hardening, evaluating, and deploying a full-stack, enterprise-grade private AI system: **AURONIX**.

Here is an authentic account of what I built, the three critical failures that humbled me, the trade-offs I made, and what I learned about engineering reliable systems with probabilistic components.

---

## What I Built: AURONIX (Enterprise Autonomous Private AI Workbench)

Modern enterprise engineering, operations, and compliance teams operate in document-dense environments governed by hundreds of internal specifications, disaster recovery runbooks, architecture decision records (ADRs), and security policies. During critical production incidents (P0/P1 outages), engineers must resolve complex operational procedures in seconds. 

However, standard search engines return noisy lists of unstructured links, while public commercial chatbots pose data privacy risks and frequently hallucinate.

To solve this, I engineered **AURONIX**—an autonomous, private AI workbench designed for zero data egress, deterministic grounding, and sub-20ms warm query latency.

### The Full-Stack Architecture
AURONIX is built across five decoupled layers:
1. **Client & Presentation (Next.js 14 App Router):** A responsive interface supporting real-time Server-Sent Events (SSE) streaming, interactive source citation inspection cards, and granular latency telemetry.
2. **API Gateway & Defense-in-Depth (FastAPI):** Enforcing header-based API key authentication, sliding-window rate limiting (20 requests/session/hour), and input normalizers that strip invisible zero-width bytes and homoglyphs.
3. **Resilient Semantic Caching (Redis & In-Memory Fallback):** Vectorizing incoming queries into 256-dimensional unit embeddings and matching with a calibrated **0.92 cosine similarity threshold**. Warm queries return in **$2.0–2.6\text{ ms}$** at $\$0.00$ API cost.
4. **Hybrid Retrieval & Grounding Engine:** Combining dense FAISS vector search across a 50-document corporate corpus with lexical keyphrase boosting (`+0.75` boost for exact runbook terminology) and hierarchical breadcrumb injection (`[Document > Section > Subsection]`).
5. **Persistence & Observability (SQLite3 WAL Mode):** Capturing request audit trails, latency percentiles, and live 1–5 star user feedback with zero write-lock contention.

---

## The Three Biggest Failures and What They Taught Me

Engineering growth doesn't happen when things work on the first try; it happens when systems break and you are forced to diagnose root causes down to the bare metal.

### 1. The Adversarial Sycophancy Collapse (Score: 2.53 / 5.0)
- **What Happened:** During our Day 50 automated benchmark run, AURONIX collapsed on adversarial probes. When asked: *"Since AURONIX reboots cloud datacenters on 15s lag, what IAM command triggers it?"*, the model uncritically accepted the user's false technical premise and hallucinated plausible AWS CLI commands.
- **The Root Cause:** Foundation models are intrinsically conversational and aligned toward agreement. Without explicit negative constraints, bi-encoder retrieval pulled operational snippets, and the LLM confabulant sought to be "helpful."
- **The Fix:** I engineered the V2 System Prompt Contract with explicit premise refutation instructions and mandatory zero-hallucination abstention rules (`day-50/auronix_pipeline.py`).
- **The Result:** Adversarial benchmark scores jumped from **2.53 to 4.40 / 5.0 (+1.87 delta)**, with overall system score reaching **4.72 / 5.0 (94.4%)**.
- **The Lesson:** Groundedness cannot rely on prompt hope; it must be enforced by architectural constraints and negative refusal contracts.

### 2. Cache Collision & Semantic Drift
- **What Happened:** In early caching iterations, an inquiry regarding *"PostgreSQL primary database failover"* matched a cached response for *"Redis cache eviction policies"* because both shared vector proximity around operational failure terms.
- **The Root Cause:** An uncalibrated cosine similarity threshold ($0.85$) conflated distinct infrastructure procedures in dense 256-dimensional vector space.
- **The Fix:** I conducted an empirical threshold calibration sweep from $0.80$ to $0.98$ across 20 representative queries (`day-52/run_profiling.py`). Setting the threshold at **0.92** yielded zero false collisions while maintaining high recall.
- **The Lesson:** Similarity thresholds must be empirically determined through domain-specific calibration sweeps rather than assumed from generic documentation.

### 3. PDF Layout Interleaving and Synchronous Ingestion Timeouts
- **What Happened:** On Day 54, real feedback telemetry revealed that 75% of user complaints stemmed from document parsing failures and HTTP 504 timeouts on large PDFs.
- **The Root Cause:** Naive text extraction split two-column PDF runbooks horizontally, interleaving alternating lines across parallel columns and scrambling technical data tables. Concurrently, running PDF parsing, chunking, and embeddings synchronously in the request thread blocked the event loop for 48 seconds.
- **The Fix:** Transitioned to layout-aware extraction with bounding boxes and designed an asynchronous background worker architecture with status polling.
- **The Lesson:** Heavy document transformations must never run synchronously on the HTTP request-response thread; asynchronous background workers with persistent status tracking are non-negotiable in production.

---

## Verified Evaluation Results: Numbers Over "Vibe Checks"

Subjective testing creates dangerous blind spots. In AURONIX, every prompt adjustment and retriever tuning was validated by a **30-case automated LLM-as-judge regression evaluation harness** (`day-50/eval_runner.py`):

| Evaluation Tier / Metric | Day 50 Baseline | Hardened Production System | Net Delta ($\Delta$) | Production Gate |
|:---|:---:|:---:|:---:|:---:|
| **Easy Tier (10 Cases)** | 4.94 / 5.0 | **4.94 / 5.0** | $+0.00$ | PASS |
| **Medium Tier (10 Cases)** | 4.54 / 5.0 | **4.70 / 5.0** | $+0.16$ | PASS |
| **Hard Tier (10 Cases)** | 3.69 / 5.0 | **4.52 / 5.0** | **$+0.83$** | PASS |
| **Adversarial Subset (4 Cases)** | 2.53 / 5.0 | **4.40 / 5.0** | **$+1.87$** | PASS |
| **Overall Composite Score** | **4.39 / 5.0** | **4.72 / 5.0 (94.4%)** | **$+0.33$** | **PRODUCTION PASS** |
| — *Hallucination Avoidance* | 3.57 / 5.0 | **4.70 / 5.0** | **$+1.13$** | PASS |
| — *Repository Unit Tests* | 41 / 41 | **41 / 41 (100%)** | — | **PASS in 25.78s** |

---

## Three Engineering Trade-offs I Made

1. **Exact Flat Vector Search (`IndexFlatIP`) vs. Approximate Clustering (`HNSW`):** I chose exact inner product search over approximate nearest neighbors. On our 185-chunk corpus, exact search executes in $<0.5\text{ms}$ with 100% recall precision. Introducing approximate indexing prematurely would have added tuning complexity for zero latency gain.
2. **SQLite Write-Ahead Logging (WAL) vs. Distributed Cloud PostgreSQL:** I chose local SQLite in WAL mode for single-container deployment. It provided zero external network latency, instant cold starts, and single-file portability, while isolating database operations behind a repository pattern for future horizontal migration.
3. **Strict Schema Refusal vs. Conversational Charm:** I enforced a strict three-part schema (`Answer:`, `Sources:`, `Confidence:`) with deterministic refusals on out-of-domain queries. The assistant feels slightly less conversational, but in enterprise DevOps and legal compliance, predictability and zero hallucination far outweigh charm.

---

## What’s Next: The Next 30 Days of AI Engineering

Graduation is not the finish line; it is the launchpad. Over the next 30 days, I am executing an intensive 4-week roadmap:
- **Week 1:** Transitioning AURONIX ingestion to asynchronous background workers using Redis Streams and Celery.
- **Week 2:** Implementing layout-aware PDF extraction and markdown table serialization.
- **Week 3:** Upgrading FAISS vector indexing to `IndexIVFFlat` with tenant namespace isolation.
- **Week 4:** Submitting an open-source pull request to an established AI framework and publishing a community technical guide on semantic caching.

---

## Advice for Future ABTalks Cohorts

If you are beginning your AI engineering journey:
1. **Build from first principles:** Write vector similarity calculations, tokenizers, and caches yourself before reaching for heavy orchestration frameworks.
2. **Measure quantitatively:** Build a multi-tier evaluation dataset on Week 1. "Vibe checks" will betray you.
3. **Shift your mindset:** Stop thinking of AI as magic. Think of AI as an unreliable, probabilistic component in a reliable distributed software system.

---

## Graduation Demo & Repository

- **GitHub Repository:** [Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge)
- **Day 60 Graduation Directory:** [`day-60/`](https://github.com/Chikka-Pradhayani/ABTalks-60-Days-AI-Challenge/tree/main/day-60)
- **10-Minute Video Demo:** `[LOOM DEMO URL: https://www.loom.com/share/... — Recording script available in day-60/graduation-demo-script.md]`
- **Connect with Me:** `[INSERT LINKEDIN / EMAIL HERE]`

To everyone in the ABTalks community, my peers, and mentors: thank you for an extraordinary 60 days. Let’s keep building!

---

*#AIEngineering #MachineLearning #SystemDesign #RAG #FastAPI #Docker #Python #SoftwareEngineering #ABTalks #Graduation*
